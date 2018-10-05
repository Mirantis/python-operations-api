from flask_oidc import OpenIDConnect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()
db = SQLAlchemy()
oidc = OpenIDConnect()
