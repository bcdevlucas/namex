import os

import requests

from flask import current_app, jsonify
from flask_restplus import Namespace, Resource, cors

from namex.utils.auth import cors_preflight, get_client_credentials, MSG_CLIENT_CREDENTIALS_REQ_FAILED
from namex.utils.api_resource import handle_exception
from namex.utils.logging import setup_logging

setup_logging()  # Important to do this first

MSG_BAD_REQUEST_NO_JSON_BODY = 'No JSON data provided'
MSG_SERVER_ERROR = 'Server Error!'
MSG_NOT_FOUND = 'Resource not found'

AUTH_SVC_URL = os.getenv('AUTH_SVC_URL', '')
AUTH_SVC_CLIENT_ID = os.getenv('AUTH_SVC_CLIENT_ID', '')
COLIN_SVC_CLIENT_SECRET = os.getenv('COLIN_SVC_CLIENT_SECRET', '')
COLIN_SVC_URL = os.getenv('COLIN_SVC_URL', '') + '/corporations/{corp_num}'


class ColinServiceException(Exception):
    def __init__(self, colin_error=None, message=None):
        # TODO: Finish this stuff
        self.error_code = int(colin_error['error_code'])
        self.colin_error_code = int(colin_error['internal_error_code'])
        self.message = message if message else str(self.colin_error_code) + ': ' + colin_error['internal_error_message']
        super().__init__(self.message)


# Register a local namespace for the NR reserve
colin_api = Namespace('colin', description='COLIN API')


@cors_preflight('POST')
@colin_api.route('/<string:corp_num>', strict_slashes=False, methods=['POST', 'OPTIONS'])
@colin_api.doc(params={
    'corp_num': 'Incorporation Number - This field is required'
})
class ColinApi(Resource):
    @cors.crossdomain(origin='*')
    def post(self, corp_num):
        try:
            authenticated, token = get_client_credentials(AUTH_SVC_URL, AUTH_SVC_CLIENT_ID, COLIN_SVC_CLIENT_SECRET)
            if not authenticated:
                raise ColinServiceException(MSG_CLIENT_CREDENTIALS_REQ_FAILED)

            # Get the profile
            print('\nCalling COLIN API using [corp_num: {corp_num}]'.format(corp_num=corp_num))
            colin_url = COLIN_SVC_URL.format(corp_num=corp_num)
            headers = {
                # 'x-api-key': COLIN_SVC_API_KEY,
                # 'Accept': 'application/xml'
            }

            print(colin_url)
            print(repr(headers))
            response = requests.get(
                colin_url,
                headers=headers
            )

            # Return the auth response if an error occurs
            if not response.status_code == 200:
                pass

            # Just return true or false, the profile either exists or it doesn't
            return jsonify(response.ok), 200
        except ColinServiceException as err:
            return handle_exception(err, err.message, err.error_code)
        except Exception as err:
            return handle_exception(err, 'Internal Server Error', 500)
