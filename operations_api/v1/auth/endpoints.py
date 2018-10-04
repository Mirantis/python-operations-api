import logging

from flask import request
from flask_restplus import Namespace, Resource
# from operations_api.app import oidc


log = logging.getLogger(__name__)


api = Namespace('auth', description='Authentication methods')


@api.route('/login')
class AuthCollection(Resource):

    def post(self):
        """
        Creates a token.
        """
        data = request.json
        return None, 200


