from pprint import pprint

from .client import SBCPaymentClient, ApiClientException
from .exceptions import SBCPaymentException
from .utils import handle_api_exception
from .request_objects.abstract import Serializable


class CalculateFeesRequest(Serializable):
    def __init__(self, **kwargs):
        self.corp_type = kwargs.get('corp_type')
        self.filing_type_code = kwargs.get('filing_type_code')
        self.jurisdiction = kwargs.get('jurisdiction', None)
        self.date = kwargs.get('date', None)
        self.priority = kwargs.get('priority', None)


def calculate_fees(req):
    try:
        # Create an instance of the API class
        api_instance = SBCPaymentClient()
        # Calculate Fees
        api_response = api_instance.calculate_fees(
            req.corp_type,
            req.filing_type_code,
            jurisdiction=req.jurisdiction,
            date=req.date,
            priority=req.priority
        )

        pprint(api_response)
        return api_response

    except ApiClientException as err:
        handle_api_exception(err, 'PaymentsApi->calculate_fees')
    except Exception as err:
        raise SBCPaymentException(err)
