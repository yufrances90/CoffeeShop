import http.client
import json

from functools import wraps

from ..utility.config import get_user_config
from ..utility.utils import verify_decode_jwt
from ..exceptions.error import AuthError

USER_CONFIG = get_user_config()

AUTH0_CLIENT_ID_I = USER_CONFIG.get('client_id')
AUTH0_CLIENT_SECRET_I = USER_CONFIG.get('client_secret')
AUTH0_AUDIENCE_I = USER_CONFIG.get('audience')
AUTH0_DOMAIN_I = USER_CONFIG.get('domain')

def request_admin_access():

    conn = http.client.HTTPSConnection(AUTH0_DOMAIN_I)

    request_object = {
        'client_id': AUTH0_CLIENT_ID_I,
        'client_secret': AUTH0_CLIENT_SECRET_I,
        'audience': AUTH0_AUDIENCE_I,
        'grant_type': 'client_credentials'
    }

    payload = json.dumps(request_object)

    headers = { 
        'content-type': "application/json" 
    }

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()

    res_json = json.loads(data.decode("utf-8"))

    return res_json

def check_permission(permission, permission_arr):

    if permission not in permission_arr:
        raise AuthError({
            'code': 'unauthorized_action',
            'description': 'Action is not authorized'
        }, 403)

    return True

def get_access_token_and_perm_arr():

    res_json = request_admin_access()

    return {
        'access_token': res_json['access_token'],
        'permission_arr': res_json['scope'].split(' ')
    }

def requires_admin_auth(permission=''):
    def requires_admin_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            res = get_access_token_and_perm_arr()

            payload = verify_decode_jwt(res['access_token'], USER_CONFIG)

            permission_arr = res['permission_arr']

            check_permission(permission, permission_arr)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_admin_auth_decorator