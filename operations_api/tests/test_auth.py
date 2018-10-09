from operations_api.tests.base import FlaskBase
from operations_api.config import settings


class TestAuthCollection(FlaskBase):
    def test_post_token_no_input_data(self):
        response = self.app.post('/api/v1/auth/login')
        assert response.status_code == 400
        assert response.json['message'] == 'Input payload validation failed'

    def test_post_token(self):
        response = self.app.post('/api/v1/auth/login',
                                 content_type='application/json',
                                 json={"password": "default", "username": "test"})
        assert response.status_code == 200
        assert 'access_token' and 'refresh_token' in response.json


class TestNegativeAuthCollection(FlaskBase):
    def setup(self):
        settings.OIDC_CLIENT_SECRETS = 'operations_api/tests/client_secrets_test.json'
        super().setup()

    def test_wrong_config(self):

        response = self.app.post('/api/v1/auth/login',
                                 content_type='application/json',
                                 json={"password": "default", "username": "test"})
        assert response.status_code == 400
        assert 'Unable to connect to keycloak server' in response.json
