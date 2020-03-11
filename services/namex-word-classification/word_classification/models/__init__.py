from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from .word_classification import WordClassification, WordClassificationSchema

db = SQLAlchemy()
ma = Marshmallow()
