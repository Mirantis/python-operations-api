import requests
import json

from flask import request
from flask_restplus import fields, Namespace, Resource as RestplusResource
from operations_api.app import oidc
from operations_api.utils.logging import ClassLoggerMixin
from requests.exceptions import ConnectionError

api = Namespace('auth', description='Authentication methods')

auth_login = api.model('AuthCollection', {
    'username': fields.String,
    'password': fields.String
})

auth_relogin = api.model('RefreshTokenCollection', {
    'refresh_token': fields.String,
})


class Resource(ClassLoggerMixin, RestplusResource):
    def __init__(self, *args, **kwargs):
        self.client_id = oidc.client_secrets['client_id']
        self.client_secret = oidc.client_secrets['client_secret']
        self.token_uri = oidc.client_secrets['token_uri']
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        super().__init__(*args, **kwargs)


@api.route('/login')
class AuthCollection(Resource):

    @api.expect(auth_login)
    def post(self):
        """
        Get token from Keycloak with user and password.
        """

        username = request.json.get('username')
        password = request.json.get('password')
        data = {'client_id': self.client_id, 'client_secret': self.client_secret,
                'grant_type': 'password', 'username': username, 'password': password}
        try:
            response = requests.post(self.token_uri, headers=self.headers, data=data)
        except ConnectionError:
            return 'Unable to connect to keycloak server. Check client_secrets config'.format(self.token_uri), 400
        return json.loads(response.text), response.status_code

    @oidc.accept_token(require_token=True)
    def get(self):
        """
        Get information of currently logged in user.
        """
        access_token = request.headers['Authorization'].split('Bearer ')[1]
        userinfo_uri = oidc.client_secrets['userinfo_uri']
        data = {'access_token': access_token}
        try:
            response = requests.post(userinfo_uri, headers=self.headers, data=data)
        except ConnectionError:
            return 'Unable to connect to keycloak server. Check client_secrets config'.format(self.token_uri), 400
        return json.loads(response.text), response.status_code


@api.route('/relogin')
class RefreshTokenCollection(Resource):

    @api.expect(auth_relogin)
    def post(self):
        """
        Get token from Keycloak with refresh token
        """

        refresh_token = request.json.get('refresh_token')
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
                }
        try:
            response = requests.post(self.token_uri, headers=self.headers, data=data)
        except ConnectionError:
            return 'Unable to connect to keycloak server. Check client_secrets config'.format(self.token_uri), 400
        return json.loads(response.text), response.status_code


@api.route('/logout')
class LogoutCollection(Resource):

    @oidc.accept_token(require_token=True)
    def post(self):
        """
        Logout user from keycloak (delete the session)
        """
        refresh_token = request.headers['Authorization'].split('Bearer ')[1]
        logout_uri = oidc.client_secrets['issuer'] + '/protocol/openid-connect/logout'
        data = {'client_id': self.client_id,
                'refresh_token': refresh_token,
                'client_secret': self.client_secret}
        try:
            response = requests.post(logout_uri, headers=self.headers, data=data)
        except ConnectionError:
            return 'Unable to connect to keycloak server. Check client_secrets config'.format(self.token_uri), 400
        return response.text, response.status_code
