import http.client
import json
import os
from dotenv import load_dotenv
from jose import jwt
from urllib.request import urlopen
from functools import wraps

from .auth import AuthError

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

AUTH0_DOMAIN_I = os.getenv('AUTH0_DOMAIN_I')
AUTH0_CLIENT_ID_I = os.getenv('AUTH0_CLIENT_ID_I')
AUTH0_CLIENT_SECRET_I = os.getenv('AUTH0_CLIENT_SECRET_I')
AUTH0_AUDIENCE_I = os.getenv('AUTH0_AUDIENCE_I')
ALGORITHMS = ['RS256']

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

def verify_decode_jwt(token):

    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN_I}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=AUTH0_AUDIENCE_I,
                issuer='https://' + AUTH0_DOMAIN_I + '/'
            )

            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def check_permission(permission, permission_arr):

    if permission not in permission_arr:
        raise AuthError({
            'code': 'unauthorized_action',
            'description': 'Action is not authorized'
        }, 403)

    return True

def requires_admin_auth(permission=''):
    def requires_admin_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            res_json = request_admin_access()

            access_token = res_json['access_token']

            payload = verify_decode_jwt(access_token)

            permission_arr = res_json['scope'].split(' ')

            check_permission(permission, permission_arr)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_admin_auth_decorator