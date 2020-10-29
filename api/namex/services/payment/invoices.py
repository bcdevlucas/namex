from __future__ import print_function
from pprint import pprint

import json
from openapi_client import ApiException

from namex.utils.auth import get_client_credentials, MSG_CLIENT_CREDENTIALS_REQ_FAILED

from . import PAYMENT_SVC_URL, PAYMENT_SVC_AUTH_URL, PAYMENT_SVC_AUTH_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET
from .client import SBCPaymentClient
from .utils import set_api_client_auth_header, set_api_client_request_host
from .exceptions import SBCPaymentException

from .request_objects.abstract import Serializable


class GetInvoiceRequest(Serializable):
    def __init__(self, **kwargs):
        self.payment_identifier = kwargs.get('payment_identifier')
        self.invoice_id = kwargs.get('invoice_id')


class GetInvoicesRequest(Serializable):
    def __init__(self, **kwargs):
        self.payment_identifier = kwargs.get('payment_identifier')


def get_invoice(payment_identifier, invoice_id):
    # Create an instance of the API class
    api_instance = SBCPaymentClient()

    authenticated, token = get_client_credentials(PAYMENT_SVC_AUTH_URL, PAYMENT_SVC_AUTH_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET)
    if not authenticated:
        raise SBCPaymentException(message=MSG_CLIENT_CREDENTIALS_REQ_FAILED)
    set_api_client_auth_header(api_instance, token)

    # Set API host URI
    set_api_client_request_host(api_instance, PAYMENT_SVC_URL)

    try:
        # Get Invoice
        api_response = api_instance.get_invoice(payment_identifier, invoice_id)

        pprint(api_response)
        return api_response

    except ApiException as err:
        print("Exception when calling InvoicesApi->get_invoice: %s\n" % err)
        err_response = json.loads(err.body)
        message = ''
        if err_response.get('detail'):
            message = err_response.get('detail')
        elif err_response.get('message'):
            message = err_response.get('message')
        raise SBCPaymentException(err, message=message)

    except Exception as err:
        print("Exception when calling InvoicesApi->get_invoice: %s\n" % err)
        raise SBCPaymentException(err)


def get_invoices(payment_identifier):
    # Create an instance of the API class
    api_instance = SBCPaymentClient()

    authenticated, token = get_client_credentials(PAYMENT_SVC_AUTH_URL, PAYMENT_SVC_AUTH_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET)
    if not authenticated:
        raise SBCPaymentException(message=MSG_CLIENT_CREDENTIALS_REQ_FAILED)
    set_api_client_auth_header(api_instance, token)

    # Set API host URI
    set_api_client_request_host(api_instance, PAYMENT_SVC_URL)

    try:
        # Get Invoices
        api_response = api_instance.get_invoices(payment_identifier)

        pprint(api_response)
        return api_response

    except ApiException as err:
        print("Exception when calling InvoicesApi->get_invoices: %s\n" % err)
        err_response = json.loads(err.body)
        message = ''
        if err_response.get('detail'):
            message = err_response.get('detail')
        elif err_response.get('message'):
            message = err_response.get('message')
        raise SBCPaymentException(err, message=message)

    except Exception as err:
        print("Exception when calling InvoicesApi->get_invoices: %s\n" % err)
        raise SBCPaymentException(err)
