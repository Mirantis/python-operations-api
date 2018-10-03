from flask_restplus import fields
from operations_api.restplus import api

ctx = api.model('Context', {
                'id': fields.Integer(readOnly=True, description='The unique identifier of a model template')})

model = api.model('Model', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a model template'),
    'name': fields.String(required=True, description='Model template name'),
    'cookiecutter_context': fields.Nested(description='Context for model generating job', model=ctx),
    'job_id': fields.String(description='Model template name'),
    'build_id': fields.String(description='Model template name'),
    'title': fields.String(description='Model template name')
})

