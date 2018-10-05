from flask import request
from flask_restplus import Namespace, Resource, fields

from operations_api.database import db  # noqa

api = Namespace('modelform', description='Model Form related operations')

forminstance = api.model('FormInstance', {
    'id': fields.String,
    'template': fields.String
})


@api.route('/template')
@api.doc(params={
    'uuid': 'Form instance ID (UUID)'
})
class ModelForm(Resource):

    def get(self):
        if request.args:
            return {'response': 'get {}'.format(request.args.get('uuid'))}
        return {'response': 'list'}

    def put(self):
        return {'response': 'created'}
