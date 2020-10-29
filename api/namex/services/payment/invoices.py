from pprint import pprint
import json

from .client import SBCPaymentClient, ApiClientException
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
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get Invoice
        api_response = api_instance.get_invoice(payment_identifier, invoice_id)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
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
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get Invoices
        api_response = api_instance.get_invoices(payment_identifier)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
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
