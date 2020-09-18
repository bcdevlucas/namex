from flask import jsonify, request, current_app
from flask_restplus import cors
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from namex.utils.logging import setup_logging
from namex.utils.auth import cors_preflight
from namex.utils.api_resource import clean_url_path_param, handle_exception

from namex.constants import NameRequestActions, NameRequestRollbackActions, RequestAction, PaymentState, PaymentStatusCode
from namex.models import Request, State, Payment

from namex.services.name_request.name_request_state import get_nr_state_actions
from namex.services.name_request.exceptions import \
    NameRequestException, InvalidInputError

from .api_namespace import api
from .api_models import nr_request
from .resource import NameRequestResource
from .utils import parse_nr_num

from namex.resources.payment.utils import build_payment_request
from namex.services.name_request.utils import has_active_payment, get_active_payment
from namex.services.payment.exceptions import SBCPaymentException
from namex.services.payment.payments import create_payment, get_payment
from openapi_client.models import PaymentRequest

setup_logging()  # Important to do this first
MSG_BAD_REQUEST_NO_JSON_BODY = 'No JSON data provided'

MSG_BAD_REQUEST_NO_JSON_BODY = 'No JSON data provided'
MSG_SERVER_ERROR = 'Server Error!'
MSG_NOT_FOUND = 'Resource not found'
MSG_ERROR_CREATING_RESOURCE = 'Could not create / update resource'


@cors_preflight('GET, PUT')
@api.route('/<int:nr_id>', strict_slashes=False, methods=['GET', 'PUT', 'OPTIONS'])
@api.doc(params={
    'nr_id': 'NR ID - This field is required'
})
class NameRequest(NameRequestResource):
    @cors.crossdomain(origin='*')
    def get(self, nr_id):
        try:
            nr_model = Request.query.get(nr_id)

            response_data = nr_model.json()
            # Add the list of valid Name Request actions for the given state to the response
            response_data['actions'] = get_nr_state_actions(nr_model.stateCd, nr_model)
            return jsonify(response_data), 200
        except Exception as err:
            return handle_exception(err, 'Error retrieving the NR.', 500)

    # REST Method Handlers
    @api.expect(nr_request)
    @cors.crossdomain(origin='*')
    def put(self, nr_id):
        """
        TODO: Test PUT with payment
        Handles general update operations including update when a payment token is present.
        NOT used for updates that only change the Name Request state. Use 'patch' instead.

        State changes handled include state changes to [DRAFT, COND_RESERVE, RESERVED, COND_RESERVE to CONDITIONAL, RESERVED to APPROVED]
        :param nr_id:
        :return:
        """
        try:
            # Find the existing name request
            nr_model = Request.query.get(nr_id)

            # Creates a new NameRequestService, validates the app config, and sets request_data to the NameRequestService instance
            self.initialize()
            nr_svc = self.nr_service

            nr_svc.nr_num = nr_model.nrNum
            nr_svc.nr_id = nr_model.id

            valid_update_states = [State.DRAFT, State.COND_RESERVE, State.RESERVED]

            # This could be moved out, but it's fine here for now
            def validate_put_request(data):
                is_valid = False
                msg = ''
                if data.get('stateCd') in valid_update_states:
                    is_valid = True

                return is_valid, msg

            is_valid_put, validation_msg = validate_put_request(self.request_data)
            validation_msg = validation_msg if not len(validation_msg) > 0 else 'Invalid request for PUT'

            if not is_valid_put:
                raise InvalidInputError(message=validation_msg)

            if nr_model.stateCd in valid_update_states:
                nr_model = self.update_nr(nr_model)

            current_app.logger.debug(nr_model.json())
            response_data = nr_model.json()
            # Add the list of valid Name Request actions for the given state to the response
            response_data['actions'] = nr_svc.current_state_actions
            return jsonify(response_data), 200
        except NameRequestException as err:
            return handle_exception(err, err.message, 500)
        except Exception as err:
            return handle_exception(err, repr(err), 500)

    def update_nr(self, nr_model):
        nr_svc = self.nr_service

        # Use apply_state_change to change state, as it enforces the State change pattern
        # apply_state_change takes the model, updates it to the specified state, and executes the callback handler
        nr_model = nr_svc.apply_state_change(nr_model, nr_model.stateCd, self.handle_nr_update)

        # This handles the updates for NRO and Solr, if necessary
        # self.add_records_to_network_services(nr_model)
        return nr_model


@cors_preflight('PUT')
@api.route('/<int:nr_id>/complete-payment', strict_slashes=False, methods=['PUT', 'OPTIONS'])
@api.doc(params={
    'nr_id': 'NR Number - This field is required'
})
class NameRequestPayment(NameRequestResource):
    # REST Method Handlers
    @api.expect(nr_request)
    @cors.crossdomain(origin='*')
    def put(self, nr_id):
        """
        TODO: Test PUT with payment
        Handles general update operations including update when a payment token is present.
        NOT used for updates that only change the Name Request state. Use 'patch' instead.

        State changes handled include state changes to [DRAFT, COND_RESERVE, RESERVED, COND_RESERVE to CONDITIONAL, RESERVED to APPROVED]
        :param nr_id:
        :return:
        """
        try:
            # Find the existing name request
            nr_model = Request.query.get(nr_id)

            # Creates a new NameRequestService, validates the app config, and sets request_data to the NameRequestService instance
            # Override the default self.initialize method
            def initialize(_self):
                # The request payload will be empty when making this call,
                # but we still want to process names, so we need to add
                # them to the request, otherwise they won't be processed!
                _self.request_data = {
                    'names': [n.as_dict() for n in nr_model.names.all()]
                }
                # Set the request data to the service
                _self.nr_service.request_data = self.request_data

            initialize(self)
            nr_svc = self.nr_service

            nr_svc.nr_num = nr_model.nrNum
            nr_svc.nr_id = nr_model.id

            valid_update_states = [State.DRAFT, State.COND_RESERVE, State.RESERVED]

            # This could be moved out, but it's fine here for now
            def validate_put_request(data, nr):
                is_valid = True
                msg = ''
                if nr.stateCd in valid_update_states:
                    is_valid = True

                return is_valid, msg

            is_valid_put, validation_msg = validate_put_request(self.request_data, nr_model)
            validation_msg = validation_msg if not len(validation_msg) > 0 else 'Invalid request for PUT'

            if not is_valid_put:
                raise InvalidInputError(message=validation_msg)

            process_payment = has_active_payment(nr_model)
            if nr_model.stateCd in valid_update_states and not process_payment:
                pass
            elif process_payment:
                # This handles updates if the NR state is DRAFT, COND_RESERVE or RESERVED
                # If the state is COND_RESERVE update state to CONDITIONAL
                # If the state is RESERVED update state to APPROVED
                # Then update the name request as required
                nr_model = self.process_payment(nr_model)

            current_app.logger.debug(nr_model.json())
            response_data = nr_model.json()
            # Add the list of valid Name Request actions for the given state to the response
            response_data['actions'] = nr_svc.current_state_actions
            return jsonify(response_data), 200
        except NameRequestException as err:
            return handle_exception(err, err.message, 500)
        except Exception as err:
            return handle_exception(err, repr(err), 500)

    def process_payment(self, nr_model):
        nr_svc = self.nr_service

        # Update the state of the payment
        payment = get_active_payment(nr_model)
        sbc_payment_response = get_payment(payment.payment_token)

        # TODO: Throw errors if this fails!
        if sbc_payment_response.status_code == PaymentStatusCode.COMPLETED.value:
            payment.payment_status_code = PaymentState.COMPLETED.value
            payment.payment_completion_date = sbc_payment_response.created_on
            payment.save_to_db()

            # Use apply_state_change to change state, as it enforces the State change pattern
            # apply_state_change takes the model, updates it to the specified state, and executes the callback handler
            if nr_model.stateCd == State.DRAFT:
                # If the state is DRAFT, leave it as a DRAFT
                nr_model = nr_svc.apply_state_change(nr_model, State.DRAFT, self.handle_nr_approval)
            if nr_model.stateCd == State.COND_RESERVE:
                # If the state is COND_RESERVE update state to CONDITIONAL, and update the name request as required
                nr_model = nr_svc.apply_state_change(nr_model, State.CONDITIONAL, self.handle_nr_approval)
            elif nr_model.stateCd == State.RESERVED:
                # If the state is RESERVED update state to APPROVED, and update the name request as required
                nr_model = nr_svc.apply_state_change(nr_model, State.APPROVED, self.handle_nr_approval)

            # This handles the updates for NRO and Solr, if necessary
            self.add_records_to_network_services(nr_model)

        return nr_model


@cors_preflight('PATCH')
@api.route('/<int:nr_id>/<string:nr_action>', strict_slashes=False, methods=['PATCH', 'OPTIONS'])
@api.doc(params={
    'nr_id': 'NR ID - This field is required',
    'nr_action': 'NR Action - One of [EDIT, UPGRADE, CANCEL, REFUND, REAPPLY, RESEND]'
})
class NameRequestFields(NameRequestResource):
    @api.expect(nr_request)
    @cors.crossdomain(origin='*')
    def patch(self, nr_id, nr_action):
        """
        Update a specific set of fields and/or a provided action. Fields excluded from the payload will not be updated.
        The following data format is expected when providing a data payload:
        { 'stateCd': 'CANCELLED' }  # Fields to update

        We use this to:
        - Edit a subset of NR fields
        - Cancel an NR
        - Change the state of an NR to [CANCELLED, INPROGRESS, HOLD, APPROVED, REJECTED
        - Apply the following actions to an NR [EDIT, UPGRADE, CANCEL, REFUND, REAPPLY, RESEND]
        :param nr_id:
        :param nr_action: One of [EDIT, UPGRADE, CANCEL, REFUND, REAPPLY, RESEND]
        :return:
        """
        try:
            # Find the existing name request
            nr_model = Request.query.get(nr_id)

            # Creates a new NameRequestService, validates the app config, and sets request_data to the NameRequestService instance
            self.initialize()
            nr_svc = self.nr_service

            nr_action = str(nr_action).upper()  # Convert to upper-case, just so we can support lower case action strings
            nr_action = NameRequestActions[nr_action].value \
                if NameRequestActions.has_value(nr_action) \
                else NameRequestActions.EDIT.value

            nr_svc.nr_num = nr_model.nrNum
            nr_svc.nr_id = nr_model.id

            valid_states = State.VALID_STATES

            # This could be moved out, but it's fine here for now
            def validate_patch_request(data):
                # Use the NR model state as the default, as the state change may not be included in the PATCH request
                request_state = data.get('stateCd', nr_model.stateCd)
                is_valid = False
                msg = ''
                # This handles updates if the NR state is 'patchable'
                if request_state in valid_states:
                    # Get the SQL alchemy columns and associations
                    is_valid = True
                else:
                    msg = 'Invalid state change requested - the NR state cannot be changed to [' + data.get('stateCd', '') + ']'

                return is_valid, msg

            is_valid_patch, validation_msg = validate_patch_request(self.request_data)
            validation_msg = validation_msg if not len(validation_msg) > 0 else 'Invalid request for PATCH'

            if not is_valid_patch:
                raise InvalidInputError(message=validation_msg)

            # if nr_model.payment_token is not None:
            #    raise NameRequestException(message='Invalid request state for PATCH - payment token should not be present!')

            def handle_patch_actions(action, model):
                return {
                    NameRequestActions.EDIT.value: self.handle_patch_edit,
                    NameRequestActions.UPGRADE.value: self.handle_patch_upgrade,
                    NameRequestActions.CANCEL.value: self.handle_patch_cancel,
                    NameRequestActions.REFUND.value: self.handle_patch_refund,
                    # TODO: This is a frontend only action throw an error!
                    # NameRequestActions.RECEIPT.value: self.patch_receipt,
                    NameRequestActions.REAPPLY.value: self.handle_patch_reapply,
                    NameRequestActions.RESEND.value: self.handle_patch_resend
                }.get(action)(model)

            # This handles updates if the NR state is 'patchable'
            nr_model = handle_patch_actions(nr_action, nr_model)

            current_app.logger.debug(nr_model.json())
            response_data = nr_model.json()
            # Add the list of valid Name Request actions for the given state to the response
            response_data['actions'] = nr_svc.current_state_actions
            return jsonify(response_data), 200

        except NameRequestException as err:
            return handle_exception(err, err.message, 500)
        except Exception as err:
            return handle_exception(err, repr(err), 500)

    def handle_patch_edit(self, nr_model):
        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, nr_model.stateCd)

        # This handles the updates for NRO and Solr, if necessary
        self.update_records_in_network_services(nr_model)
        return nr_model

    def handle_patch_upgrade(self, nr_model):
        """
        Upgrade the Name Request to priority, create the payment and save the record.
        :param nr_model:
        :return:
        """
        if not nr_model.stateCd == State.DRAFT:
            raise NameRequestException(message='Error upgrading Name Request, request is in an invalid state!')

        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, nr_model.stateCd)

        # TODO: Any other supported types? What role does frontend have in this?
        #  Also, this will generate a new payment Id and then the NR will have two payments.
        nr_name = nr_model.names[0]
        nr_applicant = nr_model.applicants[0]

        if nr_name and nr_applicant:
            payment_request = build_payment_request(nr_model)
        else:
            raise NameRequestException(message='Error upgrading Name Request, payment request is missing information!')

        try:
            # Grab the info we need off the request
            payment_info = payment_request.get('paymentInfo')
            filing_info = payment_request.get('filingInfo')
            business_info = payment_request.get('businessInfo')

            # Create our payment request
            req = PaymentRequest(
                payment_info=payment_info,
                filing_info=filing_info,
                business_info=business_info
            )

            payment_response = create_payment(req)
            if not payment_response:
                raise SBCPaymentException(message=MSG_ERROR_CREATING_RESOURCE)

            if payment_response and payment_response.status_code == PaymentStatusCode.CREATED.value:
                # Save the payment info to Postgres
                payment = Payment()
                payment.nrId = nr_model.id
                payment.payment_token = str(payment_response.id)
                payment.payment_completion_date = payment_response.created_on
                payment.payment_status_code = PaymentState.CREATED.value
                payment.save_to_db()

            nr_model.priorityCd = 'Y'
            nr_model.priorityDate = datetime.utcnow()

            # Save the name request
            nr_model.save_to_db()

        except Exception as err:
            raise NameRequestException(err, message='Error upgrading Name Request!')

        # Update the actions, as things change once the payment is successful
        self.nr_service.current_state_actions = get_nr_state_actions(nr_model.stateCd, nr_model)
        # We have not accounted for multiple payments.
        # We will need to add a request_payment model (request_id and payment_id)
        # This handles the updates for NRO and Solr, if necessary
        self.update_records_in_network_services(nr_model)
        return nr_model

    def handle_patch_reapply(self, nr_model):
        """
        Extend the Name Request's expiration date by 56 days. If the request action is set to REH or REST,
        extend the expiration by an additional year (plus the default 56 days).
        :param nr_model:
        :return:
        """
        nr_svc = self.nr_service

        if nr_model.submitCount < 3:
            if nr_model.request_action_cd in [RequestAction.REH.value, RequestAction.REN.value]:
                # If request action is REH or REST extend by 1 year (+ 56 default) days
                nr_model = nr_svc.extend_expiry_date(nr_model, (datetime.utcnow() + relativedelta(years=1,days=56)))
                nr_model = nr_svc.update_request_submit_count(nr_model)
            else:
                # Extend expiry date by (default) 56 days
                nr_model = nr_svc.extend_expiry_date(nr_model, datetime.utcnow())
                nr_model = nr_svc.update_request_submit_count(nr_model)

            # This handles updates if the NR state is 'patchable'
            nr_model = self.update_nr_fields(nr_model, nr_model.stateCd)

            # This handles the updates for NRO and Solr, if necessary
            self.update_records_in_network_services(nr_model)
        else:
            # TODO: Make a custom exception for this?
            raise NameRequestException(message='Submit count maximum of 3 retries has been reached!')

        return nr_model

    def handle_patch_resend(self, nr_model):
        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, nr_model.stateCd)

        # This handles the updates for NRO and Solr, if necessary
        # self.update_records_in_network_services(nr_model)
        return nr_model

    def handle_patch_refund(self, nr_model):
        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, nr_model.stateCd)

        # This handles the updates for NRO and Solr, if necessary
        # self.update_records_in_network_services(nr_model)
        return nr_model

    def handle_patch_cancel(self, nr_model):
        """
        Cancel the Name Request.
        :param nr_model:
        :return:
        """
        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, State.CANCELLED)

        # This handles the updates for NRO and Solr, if necessary
        self.update_records_in_network_services(nr_model)
        return nr_model

    def update_nr_fields(self, nr_model, new_state):
        """
        State changes handled:
        - to CANCELLED
        - to INPROGRESS
        - to HOLD
        - to APPROVED
        - to REJECTED
        :param nr_model:
        :param new_state:
        :return:
        """
        nr_svc = self.nr_service

        # Use apply_state_change to change state, as it enforces the State change pattern
        # apply_state_change takes the model, updates it to the specified state, and executes the callback handler
        if new_state in State.VALID_STATES:
            nr_model = nr_svc.apply_state_change(nr_model, new_state, self.handle_nr_patch)

        return nr_model


@cors_preflight('PATCH')
@api.route('/<int:nr_id>/rollback/<string:action>', strict_slashes=False, methods=['PATCH', 'OPTIONS'])
@api.doc(params={
    'nr_id': 'NR Number - This field is required',
})
class NameRequestRollback(NameRequestResource):
    @api.expect(nr_request)
    @cors.crossdomain(origin='*')
    def patch(self, nr_id, action):
        """
        Roll back a Name Request to a usable state in case of a frontend error.
        :param nr_id:
        :param action:
        :return:
        """
        try:
            # Find the existing name request
            nr_model = Request.query.get(nr_id)

            # Creates a new NameRequestService, validates the app config, and sets request_data to the NameRequestService instance
            self.initialize()
            nr_svc = self.nr_service

            nr_svc.nr_num = nr_model.nrNum
            nr_svc.nr_id = nr_model.id

            # This could be moved out, but it's fine here for now
            def validate_patch_request(data):
                # TODO: Validate the data payload
                # Use the NR model state as the default, as the state change may not be included in the PATCH request
                is_valid = False
                msg = ''
                # This handles updates if the NR state is 'patchable'
                if NameRequestRollbackActions.has_value(action):
                    is_valid = True
                else:
                    msg = 'Invalid rollback action'

                return is_valid, msg

            is_valid_patch, validation_msg = validate_patch_request(self.request_data)
            validation_msg = validation_msg if not len(validation_msg) > 0 else 'Invalid request for PATCH'

            if not is_valid_patch:
                raise InvalidInputError(message=validation_msg)

            # This handles updates if the NR state is 'patchable'
            nr_model = self.handle_patch_rollback(nr_model, action)

            current_app.logger.debug(nr_model.json())
            response_data = nr_model.json()
            # Add the list of valid Name Request actions for the given state to the response
            response_data['actions'] = nr_svc.current_state_actions
            return jsonify(response_data), 200

        except NameRequestException as err:
            return handle_exception(err, err.message, 500)
        except Exception as err:
            return handle_exception(err, repr(err), 500)

    def handle_patch_rollback(self, nr_model, action):
        """
        Roll back the Name Request.
        :param nr_model:
        :param action:
        :return:
        """
        # This handles updates if the NR state is 'patchable'
        nr_model = self.update_nr_fields(nr_model, State.CANCELLED)

        # This handles the updates for NRO and Solr, if necessary
        self.update_records_in_network_services(nr_model)
        return nr_model

    def update_nr_fields(self, nr_model, new_state):
        """
        State changes handled:
        - to CANCELLED
        :param nr_model:
        :param new_state:
        :return:
        """
        nr_svc = self.nr_service

        # Use apply_state_change to change state, as it enforces the State change pattern
        # apply_state_change takes the model, updates it to the specified state, and executes the callback handler
        if new_state in State.VALID_STATES:
            nr_model = nr_svc.apply_state_change(nr_model, new_state, self.handle_nr_patch)

        return nr_model
