from flask import request, make_response, jsonify
from flask_restplus import Namespace, Resource, cors
from flask_jwt_oidc import AuthError

from typing import Dict
from http import HTTPStatus

import requests  # noqa: I001; grouping out of order to make both pylint & isort happy
from requests import exceptions  # noqa: I001; grouping out of order to make both pylint & isort happy

from namex import jwt
from namex.exceptions import BusinessException

from . import authorized

from typing import Dict, List


class Error:  # pylint: disable=too-few-public-methods; convenience class
    """A convenience class for managing errors as code outside of Exceptions."""

    def __init__(self, code: int, message: List[Dict]):
        self.code = code
        self.msg = message


def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def validate_request():
    return True


'''
Available decorators:
- get_token_auth_header
- contains_role
- has_one_of_roles
- validate_roles
- requires_roles
- requires_auth
'''


class ResourceWithAuth(Resource):
    # Just some examples of how you could set this up to use a model or service with the resource
    _model = None
    _service = None

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, service):
        self._service = service

    def get(self, entity_id):
        if entity_id:
            entity = self.model.get_entity_by_id(entity_id)
    
            if not entity:
                return False

            return entity
        else:
            entities = self.model.find()
            return entities

    def post(self, entity):
        if not entity:
            return False

        entity = self.model.create(entity)

        return entity

    def put(self, entity_id, entity):
        entity = self.model.get_entity_by_id(entity_id)

        if not entity:
            return False

        entity = self.model.update(entity)

        return entity

    def patch(self, entity_id, data):
        entity = self.model.get_entity_by_id(entity_id)

        if not entity:
            return False

        entity = self.model.update(entity)

        return entity

    def delete(self, entity_id):
        entity = self.model.get_entity_by_id(entity_id)

        if not entity:
            return False

        if entity.delete():
            return True

        return False


def wrap_get_with_auth(get_func):
    # Inner function can access outer local functions
    def get_with_auth(*args, **kwargs):
        print("Wrapping get() with auth")

        resource = get_func(*args, **kwargs)

        if not resource:
            jsonify({'message': f'Resource not found'}), HTTPStatus.NOT_FOUND

        return jsonify(resource), HTTPStatus.OK

    return get_with_auth


def wrap_get_collection_with_auth(get_func):
    # Inner function can access outer local functions
    def get_with_auth(*args, **kwargs):
        print("Wrapping get() with auth")

        # Handle mime-types if necessary, eg: something like this for PDF
        # if str(request.accept_mimetypes) == 'application/pdf':
        #    return jsonify(
        #        {'message': _('Cannot return a single PDF of multiple resource submissions!')}
        #    ), HTTPStatus.NOT_ACCEPTABLE

        resources = get_func(*args, **kwargs)

        if len(resources) == 0:
            return jsonify(resources=[]), HTTPStatus.OK

        elif not resources:
            jsonify({'message': f'No resources found'}), HTTPStatus.NOT_FOUND

        return jsonify(resources), HTTPStatus.OK

    return get_with_auth


def wrap_post_with_auth(post_func):
    # Inner function can access outer local functions
    def post_with_auth(*args, **kwargs):
        print("Wrapping post() with auth")

        # Check authorization
        if not authorized(jwt, action=['create']):
            return jsonify({'message': _('You are not authorized to create an resource:')}), \
                HTTPStatus.UNAUTHORIZED

        json_input = request.get_json()

        resource = post_func(*args, **kwargs)

        err = validate(resource, json_input)

        if err:
            json_input['errors'] = err.msg
            return jsonify(json_input), err.code or HTTPStatus.OK

            # return jsonify(json_input), HTTPStatus.OK

        #if err_msg:
        #    reply = resource.json if resource else json_input
        #    reply['errors'] = [err_msg, ]

        #   return jsonify(reply), err_code or HTTPStatus.CREATED

        # all done

        return jsonify(resource.json), HTTPStatus.CREATED

    return post_with_auth


def wrap_put_with_auth(put_func):  # pylint: disable=too-many-return-statements
    def _put_basic_checks(resource_id, client_request):
        json_input = client_request.get_json()
        if not json_input:
            return jsonify({'message': f'No json data in body of post.'}, HTTPStatus.BAD_REQUEST)

        if resource_id and client_request.method != 'PUT':
            return jsonify({'message': f'Duplicate entry detected.'}, HTTPStatus.FORBIDDEN)

        return None, None

    # Inner function can access outer local functions
    def put_with_auth(*args, **kwargs):
        print("Wrapping put() with auth")

        # Basic checks
        # err_msg, err_code = _put_basic_checks(resource_id, request)

        # if not resource_id:
        #    return jsonify({'message': _('No resource id provided')}), HTTPStatus.BAD_REQUEST

        # Check authorization
        if not authorized(jwt, action=['edit']):
            return jsonify({'message': _('You are not authorized to replace the resource:')}), \
                HTTPStatus.UNAUTHORIZED

        err_msg, err_code = None

        if err_msg:
            return jsonify({'errors': [err_msg, ]}), err_code

        json_input = request.get_json()

        resource = put_func(*args, **kwargs)

        err = validate(resource, json_input)

        if err:
            json_input['errors'] = err.msg
            return jsonify(json_input), err.code

        if err_msg:
            reply = resource.json if resource else json_input
            reply['errors'] = [err_msg, ]

            return jsonify(reply), err_code or HTTPStatus.ACCEPTED

        # all done
        return jsonify(resource.json), HTTPStatus.ACCEPTED

    return put_with_auth


def wrap_patch_with_auth(patch_func):
    # Inner function can access outer local functions
    def patch_with_auth(resource_id, data):
        print("Wrapping patch() with auth")

        if not resource_id:
            return jsonify({'message': _('No resource id provided')}), HTTPStatus.BAD_REQUEST

        # Check authorization
        if not authorized(jwt, action=['edit']):
            return jsonify({'message': _('You are not authorized to update the resource:')}), \
                HTTPStatus.UNAUTHORIZED

        try:
            resource = patch_func(resource_id)

            if not resource:
                return jsonify({'message': _('Resource Not Found.')}), HTTPStatus.NOT_FOUND

            return jsonify(resource.json), HTTPStatus.ACCEPTED

        except (exceptions.ConnectionError, exceptions.Timeout) as err:
            # current_app.logger.error(f'Connection failure', err)
            return jsonify({'errors': [{'message': repr(err)}]}), HTTPStatus.INTERNAL_SERVER_ERROR

        except BusinessException as err:
            return jsonify({'errors': [{'error': err.error}]}), err.status_code

    return patch_with_auth


def wrap_delete_with_auth(delete_func):
    # Inner function can access outer local functions
    def delete_with_auth(*args, **kwargs):
        print("Wrapping delete() with auth")

        # if not resource_id:
        #    return jsonify({'message': _('No resource id provided')}), HTTPStatus.BAD_REQUEST

        # Check authorization
        if not authorized(jwt, action=['delete']):
            return jsonify(
                {'message': _('You are not authorized to delete the resource:')}
            ), HTTPStatus.UNAUTHORIZED

        try:
            resource = delete_func(*args, **kwargs)

            if not resource:
                return jsonify({'message': _('Resource Not Found.')}), HTTPStatus.NOT_FOUND

        except BusinessException as err:
            return jsonify({'errors': [{'error': err.error}]}), err.status_code

        # return {}, HTTPStatus.NOT_IMPLEMENTED

    return delete_with_auth


def validate(schemas, json: Dict) -> Error:  # pylint: disable=too-many-branches
    err = validate_against_schema(schemas, json)
    if err:
        return err

    msg = []

    if msg:
        return Error(HTTPStatus.BAD_REQUEST, msg)

    return None


def validate_against_schema(schemas, json_data: Dict = None) -> Error:
    valid, err = schemas.validate(json_data, 'comment')

    if valid:
        return None

    errors = []
    for error in err:
        errors.append({'path': '/'.join(error.path), 'error': error.message})

    return Error(HTTPStatus.UNPROCESSABLE_ENTITY, errors)

