import logging.config
import os

from flask import Flask

from flask_oidc import OpenIDConnect
from operations_api.database import db
from operations_api.config import settings


app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'config', 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger('operations_api')

oidc = None


def configure_app(flask_app):
    flask_app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY or os.urandom(16)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def configure_app_auth(flask_app):
    # TODO: Use parameters from config
    flask_app.config['OIDC_CLIENT_SECRETS'] = 'config/client_secrets.json'
    flask_app.config['OIDC_OPENID_REALM'] = 'Demo'
    flask_app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'bearer'
    flask_app.config['SCOPES'] = ['openid']
    flask_app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'client_secret_post'
    flask_app.config['OIDC_TOKEN_TYPE_HINT'] = 'access_token'


def initialize_app(flask_app):
    configure_app(flask_app)

    global oidc
    configure_app_auth(app)
    oidc = OpenIDConnect(app)
    from operations_api.v1 import blueprint as api
    flask_app.register_blueprint(api, url_prefix='/api/v1')
    db.init_app(flask_app)


def run():
    initialize_app(app)
    app.app_context().push()

    log.info('>>>>> Starting server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host=settings.FLASK_SERVER_HOST,
            port=int(settings.FLASK_SERVER_PORT),
            debug=settings.FLASK_DEBUG)
