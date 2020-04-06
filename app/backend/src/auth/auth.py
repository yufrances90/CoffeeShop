import json
from flask import request, _request_ctx_stack
from functools import wraps

from ..utility.config import get_auth_config
from ..utility.utils import verify_decode_jwt
from ..exceptions.error import AuthError

AUTH_CONFIG = get_auth_config()

## Auth Header

'''
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():

    request_headers = request.headers

    if request_headers is None:
        raise AuthError({
            'code': 'invalid_header', \
            'description': "No header is present"
        }, 401)

    authorization = request_headers['Authorization']

    auth_arr = authorization.split(" ")

    if "Bearer" not in auth_arr or len(auth_arr) != 2:
        raise AuthError({
            'code': 'invalid_header', \
            'description': "The header is malformed"
        }, 401)

    token = auth_arr[1]

    return token

'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_payload',
            'description': 'Permissions are not included in the payload.'
        }, 401)

    permissions = payload["permissions"]

    if permission not in permissions:
        raise AuthError({
            'code': 'unauthorized_action',
            'description': 'Action is not authorized'
        }, 403)

    return True

'''
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token, AUTH_CONFIG)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator