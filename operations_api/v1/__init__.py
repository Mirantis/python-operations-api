import logging
import traceback

from flask import Blueprint
from flask_restplus import Api
from operations_api.config import settings
from sqlalchemy.orm.exc import NoResultFound

from operations_api.v1.modelform.endpoints import api as modelform

log = logging.getLogger(__name__)

# setup api BP
blueprint = Blueprint('api', __name__)
api = Api(blueprint)

# register namespaces
api.add_namespace(modelform)


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404
