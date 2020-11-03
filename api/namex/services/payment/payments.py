from pprint import pprint

from .client import SBCPaymentClient
from .models import Payment
from .exceptions import SBCPaymentException


def get_payment(payment_identifier):
    try:
        api_instance = SBCPaymentClient()
        api_response = api_instance.get_payment(payment_identifier)
        pprint(api_response)
        return Payment(**api_response)

    except Exception as err:
        raise SBCPaymentException(err)


def create_payment(model):
    try:
        data = model.__dict__
        api_instance = SBCPaymentClient()
        api_response = api_instance.create_payment(data)
        pprint(api_response)
        return Payment(**api_response)

    except Exception as err:
        raise SBCPaymentException(err)
