from flask_restplus import Namespace, Resource

api = Namespace('modelform', description='Model Form related operations')


@api.route('/template')
class ModelForm(Resource):

    def get(self, request_id=None):
        return {'response': 'hello'}
