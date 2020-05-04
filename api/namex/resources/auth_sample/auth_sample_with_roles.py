from flask_restplus import Namespace, cors
from flask_jwt_oidc import AuthError

from urllib.parse import unquote_plus

from namex.utils.util import cors_preflight
from namex.utils.logging import setup_logging

from namex import jwt

from .resource_with_auth import \
    ResourceWithAuth, \
    handle_auth_error, validate_request, \
    wrap_get_with_auth, wrap_get_collection_with_auth, wrap_post_with_auth, wrap_put_with_auth, wrap_patch_with_auth, wrap_delete_with_auth

from .fake_model import FakeModel

setup_logging()  # It's important to do this first

# Register a local namespace for the requests
api = Namespace('authSampleWithRoles', description='Roles Example')


@api.errorhandler(AuthError)
def handle_auth_error(ex):
    return handle_auth_error(ex)


def validate_name_request():
    return validate_request()


@cors_preflight("GET, POST")
@api.route('/', strict_slashes=False, methods=['GET', 'POST', 'OPTIONS'])
class AuthorizedCollectionResourceWithRoles(ResourceWithAuth):
    _model = FakeModel

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_get_collection_with_auth
    def get(self):
        return super().get()

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_post_with_auth
    def post(self):
        return super().post(api.payload)


@cors_preflight("GET, PATCH, PUT, DELETE")
@api.route('/<string:resource_id>', strict_slashes=False, methods=['GET', 'PATCH', 'PUT', 'DELETE', 'OPTIONS'])
@api.param('resource_id', 'The resource id')
class AuthorizedResourceWithRoles(ResourceWithAuth):
    _model = FakeModel

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_get_with_auth
    def get(self, resource_id):
        return super().get(resource_id)

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_put_with_auth
    def put(self, resource_id):
        return super().put(resource_id, api.payload)

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_patch_with_auth
    def patch(self, resource_id):
        return super().patch(resource_id, api.payload)

    @api.doc(params={})
    @cors.crossdomain(
        origin='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization']
    )
    #@jwt.requires_auth
    @wrap_delete_with_auth
    def delete(self, resource_id):
        return super().delete(resource_id)
