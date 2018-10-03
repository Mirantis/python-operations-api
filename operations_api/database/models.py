from operations_api.database import db


class ModelTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
