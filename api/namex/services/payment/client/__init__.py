import requests
from enum import Enum
from functools import wraps
import os

PAYMENT_SVC_URL = os.getenv('PAYMENT_SVC_URL')
PAYMENT_SVC_AUTH_URL = os.getenv('PAYMENT_SVC_AUTH_URL')
PAYMENT_SVC_AUTH_CLIENT_ID = os.getenv('PAYMENT_SVC_AUTH_CLIENT_ID')
PAYMENT_SVC_CLIENT_SECRET = os.getenv('PAYMENT_SVC_CLIENT_SECRET')

MSG_CLIENT_CREDENTIALS_REQ_FAILED = 'Client credentials request failed'


class ApiClientException(Exception):
    def __init__(self, wrapped_err=None, message="Exception", status_code=500):
        self.err = wrapped_err
        if wrapped_err:
            self.message = '{msg}\r\n\r\n{desc}'.format(msg=message, desc=str(wrapped_err))
        else:
            self.message = message
        # Map HTTP status if the wrapped error has an HTTP status code
        self.status_code = wrapped_err.status if wrapped_err and hasattr(wrapped_err, 'status') else status_code
        super().__init__(self.message)


class ApiClientError(ApiClientException):
    def __init__(self, wrapped_err=None, message="API exception"):
        super().__init__(wrapped_err, message)


def get_client_credentials(auth_url, client_id, secret):
    auth = requests.post(
        auth_url,
        auth=(client_id, secret),
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': secret
        }
    )

    # Return the auth response if an error occurs
    if auth.status_code != 200:
        return False, auth.json()

    token = dict(auth.json())['access_token']
    return True, token


def with_authentication(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        authenticated, token = self.get_client_credentials(PAYMENT_SVC_AUTH_URL, PAYMENT_SVC_AUTH_CLIENT_ID, PAYMENT_SVC_CLIENT_SECRET)
        if not authenticated:
            raise ApiClientError(message=MSG_CLIENT_CREDENTIALS_REQ_FAILED)
        self.set_api_client_auth_header(token)
        # Set API host URI
        self.set_api_client_request_host(PAYMENT_SVC_URL)
        return func(self, *args, **kwargs)

    return wrapper


class HttpVerbs(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    PATCH = 'patch'
    OPTIONS = 'options'
    HEAD = 'head'


class ClientConfig:
    """
    The host name
    """
    _host = None
    """
    Versioning prefix like /api/v1 or whatever
    """
    _prefix = None
    """
    Request headers
    """
    _headers = None

    @property
    def host(self):
        return self._host if self._host else ''

    @host.setter
    def host(self, val):
        self._host = val

    @property
    def prefix(self):
        return self._prefix if self._prefix else ''

    @prefix.setter
    def prefix(self, val):
        self._prefix = val

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, header_arr):
        self._headers = header_arr


class BaseClient:
    def __init__(self, **kwargs):
        self.configuration = kwargs.get('configuration', ClientConfig())

    def set_api_client_auth_header(self, token):
        self.set_api_client_request_header('Authorization', 'Bearer ' + token)

    def set_api_client_request_header(self, key, value):
        self.set_default_header(key, value)

    def set_api_client_request_host(self, url):
        # Set API host URI
        self.configuration['host'] = url

    def set_default_header(self):
        pass

    def build_url(self, path):

        return self.configuration.host + self.configuration.prefix + path

    @staticmethod
    def call_api(method, url, params=None, data=None):
        try:
            if method not in HttpVerbs:
                raise ApiClientError()

            headers = {
                # If using key based auth we could do something like...
                # 'x-api-key': 'SampleKey',
            }

            response = requests.request(
                method,
                url,
                params=params,
                data=data,
                headers=headers
            )

            return response
        except Exception:
            raise


class SBCPaymentClient(BaseClient):
    def calculate_fees(self, corp_type, filing_type_code, jurisdiction=None, date=None, priority=None):
        request_url = 'fees/{corp_type}/{filing_type_code}'
        request_url = request_url.format(
            corp_type=corp_type,
            filing_type_code=filing_type_code
        )

        params = {}
        if jurisdiction:
            params['jurisdiction'] = jurisdiction
        if date:
            params['date'] = date
        if priority:
            params['priority'] = priority

        return self.call_api(HttpVerbs.GET, request_url, params=params)

    def create_payment(self, data):
        request_url = 'payment-requests'
        return self.call_api(HttpVerbs.POST, request_url, data=data)

    def get_payment(self, invoice_id):
        request_url = 'payment-requests/{invoice_id}'
        request_url = request_url.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_url)

    def get_invoices(self, invoice_id):
        """
        TODO: This is deprecated can we avoid using it?
        :return:
        """
        request_url = 'payment-requests/{invoice_id}/invoices/{invoice_id}'
        request_url = request_url.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_url)

    def generate_receipt(self, invoice_id):
        request_url = 'payment-requests/{invoice_id}/receipts'
        request_url = request_url.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.POST, request_url)

    def get_receipt(self, invoice_id):
        request_url = 'payment-requests/{invoice_id}/receipts'
        request_url = request_url.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_url)
