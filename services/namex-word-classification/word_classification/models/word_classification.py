from datetime import datetime

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import backref

from . import db, ma


class WordClassification(db.Model):
    __tablename__ = 'word_classification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classification = db.Column('word_classification', db.String(4), default='NONE', nullable=False,index=True)
    word = db.Column('word', db.String(1024), nullable=False, index=True)
    last_name_used = db.Column('last_name_used', db.String(1024))
    last_prep_name = db.Column('last_prep_name', db.String(1024))
    frequency = db.Column('frequency', db.BIGINT)
    approved_by = db.Column('approved_by', db.Integer, db.ForeignKey('users.id'))
    approved_dt = db.Column('approved_dt', db.DateTime(timezone=True))
    start_dt = db.Column('start_dt', db.DateTime(timezone=True))
    end_dt = db.Column('end_dt', db.DateTime(timezone=True))
    last_updated_by = db.Column('last_updated_by', db.Integer, db.ForeignKey('users.id'))
    last_updated_dt = db.Column('last_updated_dt', db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    approver = db.relationship('User', backref=backref('user_word_approver', uselist=False), foreign_keys=[approved_by])
    updater = db.relationship('User', backref=backref('user_word_updater', uselist=False), foreign_keys=[last_updated_by])

    def json(self):
        return {"id": self.id, "classification": self.classification, "word": self.word,
                "lastNameUsed": self. last_name_used, "lastPrepName": self.last_prep_name,
                "frequency": self.frequency,"approvedDate": self.approved_dt,
                "approvedBy": self.approved_by, "startDate": self.start_dt,
                "lastUpdatedBy": self.last_updated_by, "lastUpdatedDate": self.last_updated_dt}

    # TODO: Do we still need to update this method?
    '''
    Note: we convert to lower case as word text in the DB will be in all caps.
    '''
    @classmethod
    def find_word_classification(cls, word):
        # TODO: Can we return more than one result?
        results = cls.query.filter(func.lower(WordClassification.word) == func.lower(word))
        print(word)
        print(list(map(lambda x: x.classification, results)))
        return cls.query.filter(func.lower(WordClassification.word) == func.lower(word)).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save_to_session(self):
        db.session.add(self)


class WordClassificationSchema(ma.ModelSchema):
    class Meta:
        model = WordClassification
