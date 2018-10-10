import logging.config
import os

from flask import Flask

from operations_api.config import settings
from operations_api.extensions import cache, db, oidc  # noqa
from operations_api.v1 import blueprint as api

logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'config', 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger('operations_api')


def configure_app(flask_app):
    flask_app.config['FLASK_SERVER_HOST'] = settings.FLASK_SERVER_HOST
    flask_app.config['FLASK_SERVER_PORT'] = int(settings.FLASK_SERVER_PORT)
    flask_app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def configure_app_auth(flask_app):
    flask_app.config['OIDC_CLIENT_SECRETS'] = settings.OIDC_CLIENT_SECRETS
    flask_app.config['OIDC_OPENID_REALM'] = settings.OIDC_OPENID_REALM
    flask_app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'bearer'
    flask_app.config['SCOPES'] = ['openid']
    flask_app.config['OIDC_INTROSPECTION_AUTH_METHOD'] = 'client_secret_post'
    flask_app.config['OIDC_TOKEN_TYPE_HINT'] = 'access_token'


def configure_app_modelform(flask_app):
    modelform_keys = [key for key
                      in dir(settings)
                      if key.startswith('MODELFORM')]
    for key in modelform_keys:
        flask_app.config[key] = getattr(settings, key)


def register_extensions(flask_app):
    db.init_app(flask_app)
    oidc.init_app(flask_app)


def create_app():
    flask_app = Flask(__name__)
    configure_app(flask_app)
    configure_app_auth(flask_app)
    configure_app_modelform(flask_app)
    register_extensions(flask_app)
    flask_app.register_blueprint(api, url_prefix='/api/v1')
    flask_app.app_context().push()
    db.create_all()
    return flask_app


app = create_app()


def run():
    # TODO: remove after switching to proper database
    if app.config['ENV'] == 'development':
        db.drop_all()
    log.info('>>>>> Starting server at http://{0}:{1}/api/ <<<<<'.format(app.config['FLASK_SERVER_HOST'],
                                                                         app.config['FLASK_SERVER_PORT']))
    app.run(host=app.config['FLASK_SERVER_HOST'],
            port=app.config['FLASK_SERVER_PORT'],
            debug=settings.FLASK_DEBUG)
