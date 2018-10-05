from flask import request
from flask_restplus import Namespace, Resource, fields
from operations_api.app import db, oidc  # noqa

api = Namespace('modelform', description='Model Form related operations')

forminstance = api.model('FormInstance', {
    'id': fields.String,
    'template': fields.String
})


@api.route('/')
@api.doc(params={
    'uuid': 'Form instance ID (UUID)'
})
class ModelForm(Resource):
    @oidc.accept_token(require_token=True)
    def get(self):
        if request.args:
            return {'response': 'get {}'.format(request.args.get('uuid'))}
        return {'response': 'list'}

    def put(self):
        return {'response': 'created'}
