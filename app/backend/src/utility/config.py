import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
# refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

ALGORITHMS = ['RS256']

# auth service
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('API_AUDIENCE')

# user service [admin]
AUTH0_DOMAIN_I = os.getenv('AUTH0_DOMAIN_I')
AUTH0_CLIENT_ID_I = os.getenv('AUTH0_CLIENT_ID_I')
AUTH0_CLIENT_SECRET_I = os.getenv('AUTH0_CLIENT_SECRET_I')
AUTH0_AUDIENCE_I = os.getenv('AUTH0_AUDIENCE_I')


def get_auth_config():
    return {
        'domain': AUTH0_DOMAIN,
        'audience': API_AUDIENCE,
        'algorithms': ALGORITHMS
    }


def get_user_config():
    return {
        'domain': AUTH0_DOMAIN_I,
        'client_id': AUTH0_CLIENT_ID_I,
        'client_secret': AUTH0_CLIENT_SECRET_I,
        'audience': AUTH0_AUDIENCE_I,
        'algorithms': ALGORITHMS
    }
