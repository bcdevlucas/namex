""""word classification classifies all words in a name approved by an exmainer to be used for auto-approval

"""
from . import db, ma
import re
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func, create_engine
from sqlalchemy.orm import backref

POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = 'BVict31C'
POSTGRES_DBNAME = 'namex-auto-analyse'
#POSTGRES_DBNAME_WC = 'namex-auto-analyse'

postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=POSTGRES_USERNAME,
                                                                                        password=POSTGRES_PASSWORD,
                                                                                        ipaddress=POSTGRES_ADDRESS,
                                                                                        port=POSTGRES_PORT,
                                                                                        dbname=POSTGRES_DBNAME))

#postgres_wc_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=POSTGRES_USERNAME,
#                                                                                           password=POSTGRES_PASSWORD,
#                                                                                           ipaddress=POSTGRES_ADDRESS,
#                                                                                           port=POSTGRES_PORT,
#                                                                                           dbname=POSTGRES_DBNAME_WC))

cnx = create_engine(postgres_str)
#cnx_wc = create_engine(postgres_wc_str)


# TODO: This has been moved to WordClassification model!
def get_classification(word):
    query = 'SELECT s.word_classification FROM word_classification s WHERE lower(s.word)=' + "'" + word.lower() + "'"
    cf = pd.read_sql_query(query, cnx)

    if not cf.empty and len(cf) == 1:
        return cf['word_classification'].to_string(index=False).lower()

    return 'none'


class WordClassification(db.Model):
    __tablename__ = 'word_classification'

    # TODO: Why don't I see this in the word_classification table? I added an ID col to make this work...
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    classification = db.Column('word_classification',db.String(4),default='NONE',nullable=False,index=True)
    word = db.Column('word', db.String(1024), nullable=False, index=True)
    last_name_used = db.Column('last_name_used',db.String(1024))
    last_prep_name = db.Column('last_prep_name',db.String(1024))
    frequency = db.Column('frequency', db.BIGINT)
    approved_by = db.Column('approved_by', db.Integer, db.ForeignKey('users.id'))
    approved_dt = db.Column('approved_dt', db.DateTime(timezone=True))
    start_dt = db.Column('start_dt', db.DateTime(timezone=True))
    end_dt = db.Column('end_dt', db.DateTime(timezone=True))
    last_updated_by = db.Column('last_updated_by', db.Integer, db.ForeignKey('users.id'))
    last_updated_dt = db.Column('last_update_dt', db.DateTime(timezone=True), default=datetime.utcnow,onupdate=datetime.utcnow)

    # relationships
    approver = db.relationship('User', backref=backref('user_word_approver', uselist=False), foreign_keys=[approved_by])
    updater = db.relationship('User',backref=backref('user_word_updater', uselist=False), foreign_keys=[last_updated_by])

    def json(self):
        return {"id": self.id, "classification": self.classification, "word": self.word,
                "lastNameUsed": self. last_name_used, "lastPrepName": self.last_prep_name,
                "frequency": self.frequency,"approvedDate": self.approved_dt,
                "approvedBy": self.approved_by, "startDate": self.start_dt,
                "lastUpdatedBy": self.last_updated_by, "lastUpdateDate": self.last_update_dt}

    # TODO: Fix this it's not working...
    '''
    Note: we convert to lower case as word text in the DB will be in all caps.
    '''
    @classmethod
    def find_word_classification(cls, word):
        # TODO: Can we return more than one result?
        print(cls.query.filter(func.lower(WordClassification.word) == func.lower(word)))
        return cls.query.filter(func.lower(WordClassification.word) == func.lower(word)).first() #\
                   #.filter(or_(cls.end_dt is None, datetime.date(cls.end_dt) > date.today()))\
                   # .filter(datetime.date(cls.start_dt) <= date.today())\
                   # .filter(cls.approved_dt) <= date.today().all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def save_to_session(self):
        db.session.add(self)


class WordClassificationSchema(ma.ModelSchema):
    class Meta:
        model = WordClassification
