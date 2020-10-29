from pprint import pprint

from .client import SBCPaymentClient, ApiClientException
from .utils import handle_api_exception
from .exceptions import SBCPaymentException
from .request_objects.abstract import Serializable


class GetReceiptRequest(Serializable):
    def __init__(self, **kwargs):
        self.payment_identifier = kwargs.get('payment_identifier')


def generate_receipt(payment_identifier, model):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get receipt for the payment
        api_response = api_instance.generate_receipt(payment_identifier, model)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
        handle_api_exception(err, func_call_name='PaymentsApi->generate_receipt')
    except Exception as err:
        raise SBCPaymentException(err)


def get_receipt(payment_identifier, model):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get receipt for the payment
        api_response = api_instance.get_receipt(payment_identifier, model)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
        handle_api_exception(err, func_call_name='PaymentsApi->get_receipt')
    except Exception as err:
        raise SBCPaymentException(err)
