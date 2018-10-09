from flask import request
from flask_restplus import Namespace, Resource, fields

from operations_api.app import db, oidc  # noqa
from operations_api.database.models import FormInstance
from operations_api.v1.modelform.utils import FormTemplateCollector

api = Namespace('modelform', description='Model Form related operations')

forminstance = api.model('FormInstance', {
    'id': fields.String,
    'template': fields.String
})


@api.route('/template')
@api.doc(headers={
    'Authorization': 'Bearer {access_token}'
})
class TemplateList(Resource):

    @oidc.accept_token(require_token=True)
    @api.marshal_list_with(forminstance)
    def get(self):
        """
        Get all stored form templates.
        """
        return FormInstance.query.all(), 200

    @oidc.accept_token(require_token=True)
    @api.marshal_with(forminstance)
    @api.doc(params={
        'version': 'Form template version (optional)'
    })
    def post(self):
        """
        Generate new form template.
        """
        ftc = FormTemplateCollector()
        version = None
        if 'version' in request.args:
            versions = ftc.list_versions()
            if not request.args['version'] in versions:
                msg = 'Invalid version, valid versions are: {}'.format(', '.join(versions))
                api.abort(400, msg)
            version = request.args.get('version')
        instance = FormInstance(template=ftc.render(version))
        db.session.add(instance)
        db.session.commit()
        return instance, 200


@api.route('/template/<string:uuid>')
@api.doc(headers={
    'Authorization': 'Bearer {access_token}'
})
class Template(Resource):

    @oidc.accept_token(require_token=True)
    @api.marshal_with(forminstance)
    def get(self, uuid):
        """
        Get form template by UUID.
        """
        return FormInstance.query.get(uuid), 200


@api.route('/versions')
class Versions(Resource):

    @oidc.accept_token(require_token=True)
    def get(self):
        """
        Get all available form versions.
        """
        ftc = FormTemplateCollector()
        return {'versions': ftc.list_versions()}, 200
