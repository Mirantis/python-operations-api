from flask import current_app as app

from operations_api.database import db

from sqlalchemy_utils import EncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

SECRET_KEY = app.config['SECRET_KEY']


class FormInstance(db.Model):
    id = db.Column(UUIDType(binary=False),
                   primary_key=True)
    template = db.Column(EncryptedType(db.String,
                                       SECRET_KEY,
                                       AesEngine,
                                       'pkcs5'))
