from __future__ import print_function
from pprint import pprint

import openapi_client
# Other stuff you can import...
# from openapi_client.models import Invoice
# from openapi_client.rest import ApiException

from . import PAYMENT_SVC_URL, PAYMENT_SVC_AUTH_URL, AUTH_SVC_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET
from namex.utils.util import get_client_credentials

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
    api_instance = openapi_client.InvoicesApi()

    authenticated, token = get_client_credentials(PAYMENT_SVC_AUTH_URL, AUTH_SVC_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET)
    if not authenticated:
        raise Exception('Client credentials request failed')
    api_instance.api_client.set_default_header('Authorization', 'Bearer ' + token)

    # Set API host URI
    api_instance.api_client.configuration.host = PAYMENT_SVC_URL

    try:
        # Get Invoice
        api_response = api_instance.get_invoice(payment_identifier, invoice_id)

        pprint(api_response)
        return api_response

    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice: %s\n" % e)


def get_invoices(payment_identifier):
    # Create an instance of the API class
    api_instance = openapi_client.InvoicesApi()

    authenticated, token = get_client_credentials(PAYMENT_SVC_AUTH_URL, AUTH_SVC_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET)
    if not authenticated:
        raise Exception('Client credentials request failed')
    api_instance.api_client.set_default_header('Authorization', 'Bearer ' + token)

    # Set API host URI
    api_instance.api_client.configuration.host = PAYMENT_SVC_URL

    try:
        # Get Invoices
        api_response = api_instance.get_invoices(payment_identifier)

        pprint(api_response)
        return api_response

    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoices: %s\n" % e)
