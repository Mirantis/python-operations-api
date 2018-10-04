import uuid

from flask import current_app as app
from sqlalchemy_utils import EncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from operations_api.database import db

SECRET_KEY = app.config['SECRET_KEY']


def generate_uuid():
    return str(uuid.uuid4())


class FormInstance(db.Model):
    id = db.Column(UUIDType(binary=False),
                   primary_key=True,
                   default=generate_uuid)
    template = db.Column(EncryptedType(db.String,
                                       SECRET_KEY,
                                       AesEngine,
                                       'pkcs5'))
