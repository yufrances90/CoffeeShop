import http.client
import json

from .auth import get_access_token_and_perm_arr

from ..utility.config import get_user_config
from ..exceptions.error import AuthError

USER_CONFIG = get_user_config()

AUTH0_CLIENT_ID_I = USER_CONFIG.get('client_id')
AUTH0_CLIENT_SECRET_I = USER_CONFIG.get('client_secret')
AUTH0_AUDIENCE_I = USER_CONFIG.get('audience')
AUTH0_DOMAIN_I = USER_CONFIG.get('domain')


def request_get_all_users(access_token):

    conn = http.client.HTTPSConnection(AUTH0_DOMAIN_I)

    payload = get_payload({})

    headers = get_headers(access_token)

    conn.request("GET", "/api/v2/users", payload, headers)

    usr_list = get_response_json(conn)

    return usr_list


def request_get_all_roles(access_token):

    conn = http.client.HTTPSConnection(AUTH0_DOMAIN_I)

    payload = get_payload({})

    headers = get_headers(access_token)

    conn.request("GET", "/api/v2/roles", payload, headers)

    role_list = get_response_json(conn)

    return role_list


def get_response_json(conn):

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))


def get_payload(obj):
    return json.dumps(obj)


def get_headers(access_token):

    formatted_token = 'Bearer {}'.format(access_token)

    return {
        'Authorization': formatted_token
    }
