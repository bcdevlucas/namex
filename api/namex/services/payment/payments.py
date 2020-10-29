from pprint import pprint
import json

from .client import SBCPaymentClient, ApiClientException
from .exceptions import SBCPaymentException
from .request_objects.abstract import Serializable


class Payment(Serializable):
    """
    Sample request:
    {
        "paymentInfo": {
            "methodOfPayment": "CC"
        },
        "businessInfo": {
            "businessIdentifier": "CP1234567",
            "corpType": "NRO",
            "businessName": "ABC Corp",
            "contactInfo": {
                "city": "Victoria",
                "postalCode": "V8P2P2",
                "province": "BC",
                "addressLine1": "100 Douglas Street",
                "country": "CA"
            }
        },
        "filingInfo": {
            "filingTypes": [
                {
                    "filingTypeCode": "ABC",
                    "filingDescription": "TEST"
                },
                {
                    "filingTypeCode": "ABC"
                    ...
                }
            ]
        }
    }
    """
    def __init__(self, **kwargs):
        self.paymentInfo = kwargs.get('paymentInfo')
        self.filingInfo = kwargs.get('filingInfo')
        self.businessInfo = kwargs.get('businessInfo')


class PaymentInfo(Serializable):
    def __init__(self, **kwargs):
        self.methodOfPayment = kwargs.get('methodOfPayment', None)


class FilingInfo(Serializable):
    def __init__(self, **kwargs):
        self.corpType = kwargs.get('corpType', None)
        self.date = kwargs.get('date', None)
        self.filingTypes = kwargs.get('filingTypes', None)


class FilingType(Serializable):
    def __init__(self, **kwargs):
        self.filingTypeCode = kwargs.get('filingTypeCode', None)
        self.priority = kwargs.get('filingTypeCode', None)
        self.filingTypeDescription = kwargs.get('filingTypeDescription', None)


class BusinessInfo(Serializable):
    def __init__(self, **kwargs):
        self.businessIdentifier = kwargs.get('businessIdentifier', None)
        self.businessName = kwargs.get('businessName', None)
        self.contactInfo = kwargs.get('contactInfo', None)


class ContactInfo(Serializable):
    def __init__(self, **kwargs):
        self.firstName = kwargs.get('firstName', None)
        self.lastName = kwargs.get('lastName', None)
        self.address = kwargs.get('address', None)
        self.city = kwargs.get('city', None)
        self.province = kwargs.get('province', None)
        self.postalCode = kwargs.get('postalCode', None)


class GetPaymentRequest(Serializable):
    def __init__(self, **kwargs):
        self.payment_identifier = kwargs.get('payment_identifier')


class CreatePaymentRequest(Payment):
    pass


class UpdatePaymentRequest(Payment):
    pass


def get_payment(payment_identifier):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Get Payment
        api_response = api_instance.get_payment(payment_identifier)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
        print("Exception when calling PaymentsApi->get_payment: %s\n" % err)
        err_response = json.loads(err.body)
        message = ''
        if err_response.get('detail'):
            message = err_response.get('detail')
        elif err_response.get('message'):
            message = err_response.get('message')
        raise SBCPaymentException(err, message=message)

    except Exception as err:
        raise SBCPaymentException(err)


def create_payment(model):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Create payment records
        api_response = api_instance.create_payment(model)

        pprint(api_response)
        return api_response

    except ApiClientException as err:
        print("Exception when calling PaymentsApi->create_payment: %s\n" % err)
        err_response = json.loads(err.body)
        message = ''
        if err_response.get('detail'):
            message = err_response.get('detail')
        elif err_response.get('message'):
            message = err_response.get('message')
        raise SBCPaymentException(err, message=message)

    except Exception as err:
        raise SBCPaymentException(err)
