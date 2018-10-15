import uuid

from sqlalchemy_utils import EncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from operations_api.config import settings
from operations_api.app import db

SECRET_KEY = settings.FLASK_SECRET_KEY


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
    created_at = db.Column(db.DateTime)
