import pytest
import json

from namex.constants import NameRequestPatchActions, NameRequestPaymentActions, PaymentState
from namex.models import Request, State, Payment

from .common import API_BASE_URI, API_BASE_NAMEREQUEST_URI
# Import token and claims if you need it
# from ..common import token_header, claims
from ..common.http import build_test_query, build_request_uri
from ..common.logging import log_request_path

from tests.python.end_points.name_requests.test_setup_utils.test_helpers import create_draft_nr
from tests.python.end_points.common.http import get_test_headers

# Define our data
# Check NR number is the same because these are PATCH and call change_nr
draft_input_fields = {
    'additionalInfo': '',
    'consentFlag': None,
    'consent_dt': None,
    'corpNum': '',
    'entity_type_cd': 'CR',
    'expirationDate': None,
    'furnished': 'N',
    'hasBeenReset': False,
    # 'lastUpdate': None,
    'natureBusinessInfo': 'Test',
    # 'nrNum': '',
    # 'nwpta': '',
    # 'previousNr': '',
    # 'previousRequestId': '',
    # 'previousStateCd': '',
    'priorityCd': 'N',
    # 'priorityDate': None,
    'requestTypeCd': 'CR',
    'request_action_cd': 'NEW',
    # 'source': 'NAMEREQUEST',
    'state': 'DRAFT',
    'stateCd': 'DRAFT',
    'submitCount': 1,
    # 'submittedDate': None,
    'submitter_userid': 'name_request_service_account',
    'userId': 'name_request_service_account',
    'xproJurisdiction': ''
}


@pytest.mark.skip
def is_int_or_float(val):
    return isinstance(val, float) or isinstance(val, int)


@pytest.mark.skip
def setup_draft_nr(client):
    # Define our data
    input_fields = draft_input_fields
    post_response = create_draft_nr(client, input_fields)

    # Assign the payload to new nr var
    return json.loads(post_response.data)


@pytest.mark.skip
def verify_fees_payload(payload):
    assert isinstance(payload.get('filingFees'), float) is True
    assert isinstance(payload.get('filingType'), str) is True
    assert isinstance(payload.get('filingTypeCode'), str) is True
    assert is_int_or_float(payload.get('futureEffectiveFees')) is True
    assert is_int_or_float(payload.get('priorityFees')) is True
    assert is_int_or_float(payload.get('processingFees')) is True
    assert is_int_or_float(payload.get('serviceFees')) is True
    assert is_int_or_float(payload.get('futureEffectiveFees')) is True
    assert isinstance(payload.get('tax'), dict) is True
    assert is_int_or_float(payload.get('total')) is True


@pytest.mark.skip
def verify_payment_payload(payload):
    assert isinstance(payload.get('id'), int) is True
    assert isinstance(payload.get('nrId'), int) is True
    assert isinstance(payload.get('payment'), dict) is True
    assert isinstance(payload.get('sbcPayment'), dict) is True
    assert isinstance(payload.get('statusCode'), str) is True
    assert isinstance(payload.get('completionDate'), str) is True
    assert isinstance(payload.get('token'), str) is True


@pytest.mark.skip
def execute_calculate_regular_fees(client):
    """
    1) Get the current the fees.
    :param client:
    :return:
    """
    headers = get_test_headers()

    request_uri = API_BASE_URI + 'fees'

    # Test regular submission
    path = request_uri
    body = json.dumps({
        'corp_type': 'NRO',
        'filing_type_code': 'NM620',
        'jurisdiction': 'BC',
        'date': '',
        'priority': ''
    })
    log_request_path(path)

    response = client.post(path, data=body, headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.data)
    verify_fees_payload(payload)

    assert payload.get('filingTypeCode') == 'NM620'

    return payload


@pytest.mark.skip
def execute_calculate_upgrade_fees(client):
    """
    1) Get the current the fees.
    :param client:
    :return:
    """
    headers = get_test_headers()

    request_uri = API_BASE_URI + 'fees'

    # Test regular submission
    path = request_uri
    body = json.dumps({
        'corp_type': 'NRO',
        'filing_type_code': 'NM606',
        'jurisdiction': 'BC',
        'date': '',
        'priority': ''
    })
    log_request_path(path)

    response = client.post(path, data=body, headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.data)
    verify_fees_payload(payload)

    assert payload.get('filingTypeCode') == 'NM606'

    return payload


@pytest.mark.skip
def execute_create_payment(client, create_payment_request):
    """
    Create a payment. Automatically creates an NR for use.
    :param client:
    :param create_payment_request:
    :return:
    """
    headers = get_test_headers()

    draft_nr = setup_draft_nr(client)

    nr_id = draft_nr.get('id')
    payment_action = 'CREATE'
    # POST /api/v1/payments/<int:nr_id>/<string:payment_action>
    request_uri = API_BASE_URI + str(nr_id) + '/' + payment_action

    path = request_uri
    body = json.dumps(create_payment_request)
    log_request_path(path)

    response = client.post(path, data=body, headers=headers)

    assert response.status_code == 201

    payload = json.loads(response.data)
    verify_payment_payload(payload)

    assert payload.get('statusCode') == 'CREATED'
    assert payload.get('action') == payment_action

    return payload


@pytest.mark.skip
def execute_get_payment(client, nr_id, payment_id):
    """
    Get a payment associated with a specific NR.
    :param client:
    :param nr_id
    :param payment_id
    :return:
    """
    # GET /api/v1/payments/<int:nr_id>/payment/<int:payment_id>
    request_uri = API_BASE_URI + str(nr_id) + '/payment/' + str(payment_id)
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.get(path)

    assert response.status_code == 200

    payload = json.loads(response.data)

    assert isinstance(payload.get('id'), int) is True
    # TODO: Check invoices / receipts...
    # assert isinstance(payload.get('invoices'), list) is True

    return payload


@pytest.mark.skip
def execute_get_payments(client, nr_id):
    """
    Get all payments associated with a specific NR.
    :param client:
    :param nr_id
    :return:
    """
    # GET /api/v1/payments/<int:nr_id>
    request_uri = API_BASE_URI + str(nr_id)
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.get(path)

    assert response.status_code == 200

    payload = json.loads(response.data)

    return payload


@pytest.mark.skip
def execute_complete_payment(client, payment, action):
    """
    Complete a payment.
    :param client:
    :param payment
    :param action
    :return:
    """
    headers = get_test_headers()

    # PATCH /api/v1/payments/<int:nr_id>/payment/<int:payment_id>/<string:payment_action>
    request_uri = API_BASE_URI + str(payment.get('nrId')) + '/payment/' + str(payment.get('id')) + '/' + action
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.patch(path, data={}, headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.data)

    return payload


@pytest.mark.skip
def execute_refund_payment(client, payment):
    """
    Refund a payment.
    :param client:
    :param payment
    :return:
    """
    headers = get_test_headers()

    request_uri = API_BASE_URI + \
        str(payment.get('nrId')) + '/payment/' + str(payment.get('id')) + '/' + \
        NameRequestPaymentActions.REQUEST_REFUND.value
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.patch(path, data={}, headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.data)

    return payload


@pytest.mark.skip
def execute_cancel_and_refund_all_payments(client, nr_id):
    """
    Cancel NR and request refund for all NR payments.
    :param client
    :param nr_id
    :return:
    """
    headers = get_test_headers()

    request_uri = API_BASE_NAMEREQUEST_URI + str(nr_id) + '/' + NameRequestPatchActions.REQUEST_REFUND.value
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.patch(path, json={}, headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.data)

    return payload


@pytest.mark.skip
def execute_get_receipt(client, payment_id):
    """
    Get the receipt.
    :param client:
    :param payment_id:
    :return:
    """
    request_uri = API_BASE_URI + str(payment_id) + '/receipt'
    test_params = [{}]

    query = build_test_query(test_params)
    path = build_request_uri(request_uri, query)
    log_request_path(path)

    response = client.get(path)

    assert response.status_code == 200

    payload = json.loads(response.data)

    assert isinstance(payload.get('filingFees'), int) is True
    assert isinstance(payload.get('filingType'), str) is True
    assert isinstance(payload.get('filingTypeCode'), str) is True
    assert isinstance(payload.get('processingFees'), int) is True
    assert isinstance(payload.get('tax'), list) is True


def test_payment_fees(client):
    regular_fees = execute_calculate_regular_fees(client)
    print('Regular fees: \n' + json.dumps(regular_fees))
    upgrade_fees = execute_calculate_upgrade_fees(client)
    print('Upgrade fees: \n' + json.dumps(upgrade_fees))


def test_create_payment(client):
    create_payment_request = {
        'paymentInfo': {
            'methodOfPayment': 'CC'
        },
        'businessInfo': {
            'corpType': 'NRO',
            'businessIdentifier': 'NR L000001',
            'businessName': 'ABC PLUMBING LTD.',
            'contactInfo': {
                'addressLine1': '1796 KINGS RD',
                'city': 'VICTORIA',
                'province': 'BC',
                'country': 'CA',
                'postalCode': 'V8R 2P1'
            }
        },
        'filingInfo': {
            'date': '2020-09-02',
            'filingTypes': [
                {
                    'filingTypeCode': 'NM620',
                    'priority': False,
                    'filingDescription': ''
                }
            ]
        }
    }

    payment = execute_create_payment(client, create_payment_request)
    return payment


def test_payment_completion(client):
    try:
        test_payment_fees(client)
        payment = test_create_payment(client)
        payment_id = payment['id']
        nr_id = payment['nrId']

        # Fire off the request to complete the payment, just to test that the endpoint is there and runs,
        # we will not actually be able to complete the payment without a browser (at this time anyway)
        execute_complete_payment(client, payment, NameRequestPaymentActions.COMPLETE.value)
        # Manually update the Payment, setting the stateCd to COMPLETE
        payment_model = Payment.query.get(payment_id)
        payment_model.payment_status_code = PaymentState.COMPLETED.value
        payment_model.save_to_db()
        # Get the 'completed' payment
        completed_payment = execute_get_payment(client, nr_id, payment_id)

        assert payment_id == completed_payment['id']
        assert completed_payment['statusCode'] == PaymentState.COMPLETED.value
    except Exception as err:
        print(repr(err))
        raise err


def test_payment_refund(client):
    """
    eg.
    curl -i -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" https://pay-api-dev.pathfinder.gov.bc.ca/api/v1/payment-requests/5979/refunds
    curl -i -X POST -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJUbWdtZUk0MnVsdUZ0N3FQbmUtcTEzdDUwa0JDbjF3bHF6dHN0UGdUM1dFIn0.eyJleHAiOjE2MDY3OTIzOTUsImlhdCI6MTYwNjc3NDM5NSwianRpIjoiMzU0ZDFhNDctODllYS00OWMwLWE0NmUtNTNjNmY5ZWQ5MzYyIiwiaXNzIjoiaHR0cHM6Ly9kZXYub2lkYy5nb3YuYmMuY2EvYXV0aC9yZWFsbXMvZmNmMGtwcXIiLCJhdWQiOlsiTmFtZVgtRGV2IiwiZW50aXR5LXNlcnZpY2VzIiwic2JjLWF1dGgtd2ViIiwiYWNjb3VudC1zZXJ2aWNlcyIsImFjY291bnQiXSwic3ViIjoiMWMxNjA0ODktNWE1NS00MWUzLTg3NzMtOGQ5ODRhMGZlMDY4IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibmFtZS1yZXF1ZXN0LXNlcnZpY2UtYWNjb3VudCIsInNlc3Npb25fc3RhdGUiOiI0OGE3YjRiNi0zZDI4LTQzMjItODNhZS1hYmI5YWNhZGU5MzciLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbInN5c3RlbSIsImVkaXQiLCJuYW1lc192aWV3ZXIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJuYW1leC1zY29wZSIsImNvcnBfdHlwZSI6Ik5SIiwiY2xpZW50SG9zdCI6Ijk2LjU0LjIyNi4yMTQiLCJjbGllbnRJZCI6Im5hbWUtcmVxdWVzdC1zZXJ2aWNlLWFjY291bnQiLCJyb2xlcyI6WyJzeXN0ZW0iLCJlZGl0IiwibmFtZXNfdmlld2VyIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJjbGllbnRBZGRyZXNzIjoiOTYuNTQuMjI2LjIxNCIsInVzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LW5hbWUtcmVxdWVzdC1zZXJ2aWNlLWFjY291bnQifQ.ZoM1BkQPrx0rmio4QCgnJpodR_q-5UdYJKL-jaq70aRSIZHy3DYi28ejhyLMI5SxxxnGHtFKZkFkLObzgKZdJ8m7fqq6xgZ3GMLTVl2nBvSsPIhPGD1vF0vxctWWTq8Q16mjHzBKp23PeiqxQvV0YTX_ln8SoTjy-kl4DrZIDobFeP5pOETTN6riMW0jIWU7mqjyS8NHGLFvo17g71Il1QRbdfMMyIAFjqBQkbknvtQjXefJxX_3UOt-z8BCwRSJafdLzR4HvyAyOZxNOpdrIVjHSnE_RmUIr3yz8YABjUmA_-uZivjyU8y7vkKX_N9ZHcYxFE1BFCVWAuApN_gvuQ" -H "Content-Type: application/json" https://pay-api-dev.pathfinder.gov.bc.ca/api/v1/payment-requests/5979/refunds
    :param client:
    :return:
    """
    try:
        test_payment_fees(client)
        payment = test_create_payment(client)
        payment_id = payment['id']
        nr_id = payment['nrId']

        # Get the NR, we created one when we generated the test payment
        # nr = Request.query.get(payment['nrId'])

        # Fire off the request to complete the payment, just to test that the endpoint is there and runs,
        # we will not actually be able to complete the payment without a browser (at this time anyway)
        execute_complete_payment(client, payment, NameRequestPaymentActions.COMPLETE.value)
        # Manually update the Payment, setting the stateCd to COMPLETE
        payment_model = Payment.query.get(payment_id)
        payment_model.payment_status_code = PaymentState.COMPLETED.value
        payment_model.save_to_db()
        # Get the 'completed' payment
        completed_payment = execute_get_payment(client, nr_id, payment_id)

        assert payment_id == completed_payment['id']

        updated_nr = execute_refund_payment(client, payment)

        assert updated_nr.get('stateCd') == State.REFUND_REQUESTED
        # Make sure there are no actions, this state is identical to CANCELLED except there's a refund request too
        assert updated_nr.get('actions') is None

        # Get any payments and make sure they
        payments = execute_get_payments(client, completed_payment['nrId'])
        assert payments and isinstance(payments, list) and len(payments) == 1
        assert payments[0]['statusCode'] == State.REFUND_REQUESTED
    except Exception as err:
        print(repr(err))
        raise err


def test_cancel_and_refund(client):
    try:
        test_payment_fees(client)
        payment = test_create_payment(client)
        payment_id = payment['id']
        nr_id = payment['nrId']

        # Get the NR, we created one when we generated the test payment
        # nr = Request.query.get(payment['nrId'])

        # Fire off the request to complete the payment, just to test that the endpoint is there and runs,
        # we will not actually be able to complete the payment without a browser (at this time anyway)
        execute_complete_payment(client, payment, NameRequestPaymentActions.COMPLETE.value)
        # Manually update the Payment, setting the stateCd to COMPLETE
        payment_model = Payment.query.get(payment_id)
        payment_model.payment_status_code = PaymentState.COMPLETED.value
        payment_model.save_to_db()
        # Get the 'completed' payment
        completed_payment = execute_get_payment(client, nr_id, payment_id)

        assert payment_id == completed_payment['id']

        updated_nr = execute_cancel_and_refund_all_payments(client, completed_payment['nrId'])

        assert updated_nr.get('stateCd') == State.REFUND_REQUESTED
        # Make sure there are no actions, this state is identical to CANCELLED except there's a refund request too
        assert updated_nr.get('actions') is None

        # Get any payments and make sure they
        payments = execute_get_payments(client, completed_payment['nrId'])
        assert payments and isinstance(payments, list) and len(payments) == 1
        assert payments[0]['statusCode'] == State.REFUND_REQUESTED
    except Exception as err:
        print(repr(err))
        raise err


@pytest.mark.skip
def test_payment_receipt(client):
    try:
        test_payment_completion(client)
        # TODO: Not sure how to test this... still working on it...
        # payment_receipt = execute_get_receipt(client, payment['id'])
    except Exception as err:
        print(repr(err))
        raise err
