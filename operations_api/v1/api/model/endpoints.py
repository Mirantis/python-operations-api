import logging

from flask import request
from flask_restplus import Resource
from operations_api.database.models import ModelTemplate
from operations_api.v1.api.model.serializers import model
from operations_api.v1.api.model.operations import create_model
from operations_api.restplus import api


log = logging.getLogger(__name__)

ns = api.namespace('models', description='Reclass template related operations')


@ns.route('/')
class ModelCollection(Resource):

    # @api.marshal_list_with(model)
    def get(self):
        """
        Returns list of all created models.
        """
        pass

    @api.response(200, 'Model successfully created.')
    @api.expect(model)
    def post(self):
        """
        Creates a model.
        """
        data = request.json
        create_model(data)
        return None, 200


@ns.route('/<int:id>')
@api.response(404, 'Model not found.')
class ModelItem(Resource):

    @api.marshal_with(model)
    def get(self, id):
        """
        Returns a model template with specified id.
        """
        return ModelTemplate.query.filter(ModelTemplate.id == id).one()
