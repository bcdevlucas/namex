from pprint import pprint
from datetime import datetime

from .client import SBCPaymentClient
from .exceptions import SBCPaymentException
from .models import ReceiptResponse
from .models.abstract import Serializable


class GetReceiptRequest(Serializable):
    def __init__(self, **kwargs):
        self.payment_identifier = kwargs.get('payment_identifier')


def generate_receipt(payment_identifier, data):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()

        # Get receipt for the payment
        api_response = api_instance.generate_receipt(payment_identifier, data.as_dict())
        return api_response

    except Exception as err:
        raise SBCPaymentException(err)


def get_receipt(payment_identifier):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get receipt for the payment
        api_response = api_instance.get_receipt(payment_identifier)

        pprint(api_response)
        return ReceiptResponse(**api_response)

    except Exception as err:
        raise SBCPaymentException(err)
