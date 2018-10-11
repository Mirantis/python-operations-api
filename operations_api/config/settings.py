import json
import os

# Flask settings
FLASK_SERVER_HOST = 'localhost'
FLASK_SERVER_PORT = '8001'
FLASK_DEBUG = True
FLASK_SECRET_KEY = 'secretsecretsecret'
FLASK_LOG_CONFIG = 'config/logger_config.yml'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'cockroachdb://oapi@localhost:26257/oapi'
SQLALCHEMY_ECHO = FLASK_DEBUG
# Turn off the Flask-SQLAlchemy event system
SQLALCHEMY_TRACK_MODIFICATIONS = False

OIDC_CLIENT_SECRETS = 'operations_api/config/client_secrets.json'
OIDC_OPENID_REALM = 'Demo'

# Override default settings with local_settings
try:
    from operations_api.local_settings import *  # noqa
except ImportError:
    pass

# Override both default and local settings with env variables with prefix OAPI_
_locals = locals()
for key, value in os.environ.items():
    if key.startswith('OAPI_'):
        _key = key[5:]
        try:
            _value = json.loads(value)
        except Exception:
            _value = value
        _locals[_key] = _value
