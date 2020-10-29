from pprint import pprint
import json

from .client import SBCPaymentClient, ApiClientException
from .exceptions import SBCPaymentException
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
        print("Exception when calling FeesApi->calculate_fees: %s\n" % err)
        err_response = json.loads(err.body)
        message = ''
        if err_response.get('detail'):
            message = err_response.get('detail')
        elif err_response.get('message'):
            message = err_response.get('message')
        raise SBCPaymentException(err, message=message)

    except Exception as err:
        raise SBCPaymentException(err)
