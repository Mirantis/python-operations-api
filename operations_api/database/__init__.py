from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def reset_database():
    from operations_api.database.models import ModelTemplate # noqa
    db.drop_all()
    db.create_all()
