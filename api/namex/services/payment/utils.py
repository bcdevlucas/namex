import json
from .exceptions import SBCPaymentException


def set_api_client_auth_header(api_instance, token):
    set_api_client_request_header(api_instance, 'Authorization', 'Bearer ' + token)


def set_api_client_request_header(api_instance, key, value):
    api_instance.api_client.set_default_header(key, value)


def set_api_client_request_host(api_instance, url):
    # Set API host URI
    api_instance.api_client.configuration.host = url


def handle_api_exception(err, func_call_name='function'):
    print('Exception when calling {func}: \n{err}'.format(func=func_call_name, err=err))
    err_response = json.loads(err.body)
    message = ''
    if err_response.get('detail'):
        message = err_response.get('detail')
    elif err_response.get('message'):
        message = err_response.get('message')
    raise SBCPaymentException(err, message=message)
