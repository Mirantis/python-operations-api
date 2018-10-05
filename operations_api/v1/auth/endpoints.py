import requests
import json

from flask import request
from flask_restplus import Namespace, Resource, fields
from operations_api.app import oidc


api = Namespace('auth', description='Authentication methods')

auth = api.model('AuthCollection', {
    'username': fields.String,
    'password': fields.String
})


@api.route('/login')
class AuthCollection(Resource):
    @api.expect(auth)
    def post(self):
        """
        Creates a token.
        """
        client_id = oidc.client_secrets['client_id']
        client_secret = oidc.client_secrets['client_secret']
        grant_type = 'password'

        token_uri = oidc.client_secrets['token_uri']
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        username = request.json.get("username")
        password = request.json.get("password")
        data = {"client_id": client_id, "client_secret": client_secret,
                "grant_type": grant_type, "username": username, "password": password}
        response = requests.post(token_uri, headers=headers, data=data)

        return json.loads(response.text), response.status_code
