import ast
import jenkins
import json
import yaml

from datetime import datetime
from flask import current_app as app, request
from flask_restplus import fields, Namespace, Resource as RestplusResource

from operations_api import exceptions
from operations_api.app import db, oidc  # noqa
from operations_api.database.models import FormInstance
from operations_api.utils.logging import ClassLoggerMixin
from operations_api.v1.modelform.utils import FormTemplateCollector


class ValidJSON(fields.Raw):
    def format(self, value):
        return json.dumps(ast.literal_eval(value))


api = Namespace('modelform', description='Model Form related operations')

forminstance = api.model('FormInstance', {
    'id': fields.String,
    'template': ValidJSON(attribute='template'),
    'created_at': fields.DateTime
})


class Resource(ClassLoggerMixin, RestplusResource):
    pass


@api.route('/templates')
@api.doc(headers={
    'Authorization': 'Bearer {access_token}'
})
class TemplateList(Resource):

    # @oidc.accept_token(require_token=True)
    @api.marshal_list_with(forminstance)
    def get(self):
        """
        Get all stored form templates.
        """
        _list = FormInstance.query.all()
        self.logger.debug('objects: {}, count: {}'.format(_list, len(_list)))
        return FormInstance.query.all(), 200

    # @oidc.accept_token(require_token=True)
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
        created_at = datetime.utcnow().replace(microsecond=0)
        instance = FormInstance(template=ftc.render(version), created_at=created_at)
        db.session.add(instance)
        db.session.commit()
        self.logger.debug('object: {}'.format(instance))
        return instance, 200


@api.route('/templates/<string:uuid>')
@api.doc(headers={
    'Authorization': 'Bearer {access_token}'
})
# TODO: Add uuid validation
class Template(Resource):

    # @oidc.accept_token(require_token=True)
    @api.marshal_with(forminstance)
    def get(self, uuid):
        """
        Get form template by UUID.
        """
        instance = FormInstance.query.get(uuid)
        self.logger.debug('object: {}'.format(instance))
        return instance, 200

    # @oidc.accept_token(require_token=True)
    def delete(self, uuid):
        """
        Delete form template by UUID.
        """
        instance = FormInstance.query.get(uuid)
        db.session.delete(instance)
        db.session.commit()
        self.logger.debug('object: {}'.format(instance))
        return 'Object with {0} deleted successfully'.format(uuid), 200


@api.route('/versions')
class Versions(Resource):

    # @oidc.accept_token(require_token=True)
    def get(self):
        """
        Get all available form versions.
        """
        ftc = FormTemplateCollector()
        versions = ftc.list_versions()
        self.logger.debug('object: {}'.format(versions))
        return {'versions': versions}, 200


@api.route('/submit')
class Submit(Resource):

    @property
    def jenkins(self):
        keys = ['MODELFORM_JENKINS_URL', 'MODELFORM_JENKINS_USERNAME', 'MODELFORM_JENKINS_PASSWORD']
        if all(k in app.config for k in keys):
            return jenkins.Jenkins(
                app.config['MODELFORM_JENKINS_URL'],
                username=app.config['MODELFORM_JENKINS_USERNAME'],
                password=app.config['MODELFORM_JENKINS_PASSWORD'])
        else:
            msg = 'Configuration keys {}, {} and {} are required.'.format(keys)
            raise exceptions.ImproperlyConfigured(msg)

    # @oidc.accept_token(require_token=True)
    def post(self):
        """
        Construct Jenkins pipeline context with default context and
         form data from request data.
        """
        # Get form data
        form_data = request.json or {}

        # Map default context variables required by pipeline
        #  into the response dict and merge form data over it
        default_context = {
            'mcp_version': app.config.get('MODELFORM_MCP_VERSION', '2018.8.0'),
            'shared_reclass_url': app.config.get('MODELFORM_SHARED_RECLASS_URL',
                                                 'https://github.com/Mirantis/reclass-system-salt-model.git'),
            'shared_reclass_branch': app.config.get('MODELFORM_SHARED_RECLASS_BRANCH', '2018.8.0'),
            'cluster_domain': app.config.get('MODELFORM_CLUSTER_DOMAIN', 'deploy-name.local'),
            'cluster_name': app.config.get('MODELFORM_CLUSTER_NAME', 'deployment_name'),
            'salt_master_hostname': app.config.get('MODELFORM_SALT_MASTER_HOSTNAME', 'cfg01'),
            'local_repositories': app.config.get('MODELFORM_LOCAL_REPOSITORIES', False),
            'offline_deployment': app.config.get('MODELFORM_OFFLINE_DEPLOYMENT', False),
            # TODO: change default template_url after import to Mirantis namespace
            'cookiecutter_template_url': app.config.get('MODELFORM_COOKIECUTTER_TEMPLATE_URL',
                                                        'https://github.com/LotharKAtt/cookiecutter-trymcp.git'),
            'cookiecutter_template_branch': app.config.get('MODELFORM_COOKIECUTTER_TEMPLATE_BRANCH', 'master')
        }
        default_context.update(form_data)

        for key, value in default_context.items():
            if isinstance(value, bool):
                default_context[key] = str(value)

        template_context = {'default_context': default_context}

        # Setup Jenkins pipeline, by overriding default values with template
        #  context values of the same name
        pipeline_context = {
            'COOKIECUTTER_TEMPLATE_CONTEXT': yaml.safe_dump(template_context)
        }
        default_pipeline_context = {
            'DISTRIB_REVISION': 'proposed',
            'EMAIL_ADDRESS': '',
            'TEST_MODEL': True
        }
        additional_context = app.config.get('MODELFORM_PIPELINE_CONTEXT', default_pipeline_context)
        pipeline_context.update(additional_context)
        for key in pipeline_context:
            if key.lower() in default_context and default_context.get(key.lower(), None):
                pipeline_context[key] = default_context[key.lower()]

        pipeline_name = app.config.get('MODELFORM_PIPELINE_NAME', )
        if not pipeline_name:
            msg = 'Configuration key MODELFORM_PIPELINE_NAME is required'
            raise exceptions.ImproperlyConfigured(msg)

        result = self.jenkins.build_job(pipeline_name, pipeline_context)
        if result:
            return {'message': 'pipeline started'}, 200
        return {'message': 'no response from Jenkins server'}, 500
