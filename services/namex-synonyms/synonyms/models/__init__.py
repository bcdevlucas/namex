from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from .synonym import Synonym, SynonymSchema

db = SQLAlchemy()
ma = Marshmallow()
