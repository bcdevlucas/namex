import re
from . import db, ma

from enum import Enum

import pandas as pd
from sqlalchemy import create_engine

from namex.services.name_request.auto_analyse.name_analysis_utils import get_dataframe_list, get_flat_list
from ..services.name_request.auto_analyse import DataFrameFields
from namex.constants import AllEntityTypes


# The class that corresponds to the database table for synonyms.
class Synonym(db.Model):
    __tablename__ = 'synonym'
    __bind_key__ = 'synonyms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100))
    synonyms_text = db.Column(db.String(1000), unique=True, nullable=False)
    stems_text = db.Column(db.String(1000), nullable=False)
    comment = db.Column(db.String(1000))
    enabled = db.Column(db.Boolean(), default=True)

    def json(self):
        return {"id": self.id, "category": self.category, "synonymsText": self.synonyms_text,
                "stemsText": self.stems_text, "comment": self.comment, "enabled": self.enabled}

    # TODO: Does this belong here?
    @classmethod
    def get_designation_by_entity_type(cls, entity_type):
        query = 'SELECT s.category, s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^' + entity_type.lower() + '.*(english[_ -]+)+designation[s]?[_-]' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            designation_value_list = {
                re.sub(r'.*(any).*|.*(end).*', r'\1\2', x[0], 0, re.IGNORECASE): ''.join(x[1:]).split(",") for x in
                df.itertuples(index=False)}
            return designation_value_list

        return None

    # TODO: Does this belong here?
    @classmethod
    def get_entity_type_by_value(cls, entity_type_dicts, designation):
        entity_list = list()
        entity__designation_end_list = entity_type_dicts.items()
        print(entity__designation_end_list)
        for entity_designation in entity__designation_end_list:
            if any(designation in value for value in entity_designation[1]):
                entity_list.append(entity_designation[0])
        return entity_list

    @classmethod
    def find(cls, term, col):
        print('finding {} for {}'.format(col, term))
        synonyms_list = []
        term = term.lower()
        if col == 'synonyms_text':
            rows = cls.query.filter(Synonym.synonyms_text.ilike('%' + term + '%')).all()
            for row in rows:
                synonyms = [synonym.strip().lower() for synonym in row.synonyms_text.split(',')]
                if term in synonyms:
                    synonyms_list.append(row)
        # col == stems_text
        else:
            rows = cls.query.filter(Synonym.stems_text.ilike('%' + term + '%')).all()
            for row in rows:
                synonyms = [synonym.strip().lower() for synonym in row.stems_text.split(',')]
                if term in synonyms:
                    synonyms_list.append(row)

        return synonyms_list

    @classmethod
    def is_substitution_word(cls, word):
        df = pd.read_sql_query(
            'SELECT s.synonyms_text FROM synonym s where lower(s.category) LIKE ' + "'" + '%% ' + "sub'" + 'and ' + \
            's.synonyms_text ~ ' + "'" + '\\y' + word.lower() + '\\y' + "'", con=db.engine)
        if not df.empty:
            return True
        return False

    @classmethod
    def get_substitution_list(cls, word=None):
        if word:
            query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) LIKE ' + "'" + '%% ' + "sub'" + ' AND ' + \
                    's.synonyms_text ~ ' + "'" + '\\y' + word.lower() + '\\y' + "';"
        else:
            query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) LIKE ' + "'" + '%% ' + "sub'"

        df = pd.read_sql_query(query, con=db.engine)
        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    @classmethod
    def get_synonym_list(cls, word=None):
        if word:
            return cls.query_category('!~* ' + "'" + '\w*(sub|stop)\s*$' + "'" + ' AND ' + 's.synonyms_text ~ ' + "'" + '\\y' + word.lower() + '\\y' + "';")

    @classmethod
    def get_stop_word_list(cls):
        return cls.query_category('~ ' + "'" + '^stop[_ -]+word[s]?' + "'")

    @classmethod
    def get_prefix_list(cls):
        return cls.query_category('~ ' + "'" + '^prefix(es)?' + "'")

    @classmethod
    def get_en_designation_any_all_list(cls):
        return cls.query_category('~ ' + "'" + '^(english[_ -]+)?designation[s]?[_-]any' + "'")

    @classmethod
    def get_en_designation_end_all_list(cls):
        return cls.query_category('~ ' + "'" + '^english[_ -]+designation[s]?[_-]+end' + "'")

    @classmethod
    def get_fr_designation_end_list(cls):
        return cls.query_category("'" + '(?=french[/_ -]+designation[s]?[/_-]+end)' + "'")

    @classmethod
    def get_stand_alone_list(cls):
        return cls.query_category('~ ' + "'" + '(?=stand[/_ -]?alone)' + "'")

    @classmethod
    def query_category(cls, category_query):
        # TODO: Raise error if category not provided or None or empty
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ' + category_query
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: Use real code types and complete this, so we can get rid of all the permutations...
    #  This should be okay with a string like "'" + '^ll.*(english[_ -]+)+designation[s]?[_-]end' + "'"
    #  I haven't worked out the other possibilities that are still in this class...
    @classmethod
    def get_entity_type_designation(cls, entity_type_code, position_code, lang='english'):
        code_str = entity_type_code.value
        position_str = position_code.value
        query = ''

        if code_str == AllEntityTypes.ALL.value:
            query = "'" + '^' + lang.lower() + '[_ -]+designation[s]?[_-]+' + position_str.lower() + "'"
        else:
            query = "'" + '^' + code_str.lower() + '.*(' + lang.lower() + '[_ -]+)+designation[s]?[_-]' + position_str.lower() + "'"

        results = cls.query_category(query)
        return results

    # TODO: Use real code types and complete this, so we can get rid of all the permutations
    @classmethod
    def get_entity_type_designations(cls, entity_type_codes, position_code, lang='english'):
        designations = dict.fromkeys(map(lambda c: c.value, entity_type_codes), [])

        for code in entity_type_codes:
            code_str = code.value
            designations[code_str] = cls.get_entity_type_designation(code, position_code, lang)

        return designations
    
    '''
    TODO: All these following methods could be refactored into a single method, really...
    '''
    
    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_CC_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^cc.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_UL_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^ul.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_BC_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^bc.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None
    
    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_CR_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^cr.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_CP_entity_type_any_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^cp.*(english[_ -]+)+designation[s]?[_-]any' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_XCP_entity_type_any_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^xcp.*(english[_ -]+)+designation[s]?[_-]any' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None
    
    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_CC_entity_type_any_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^cc.*(english[_ -]+)+designation[s]?[_-]any' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None
    
    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_fr_designation_end_list(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '(?=french[/_ -]+designation[s]?[/_-]+end)' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_RLC_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^rlc.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None

    # TODO: These are ALL the same method, with a single different type... consolidate these functions!
    @classmethod
    def get_en_LL_entity_type_end_designation(cls):
        query = 'SELECT s.synonyms_text FROM synonym s WHERE lower(s.category) ~ ' + "'" + '^ll.*(english[_ -]+)+designation[s]?[_-]end' + "'"
        df = pd.read_sql_query(query, con=db.engine)

        if not df.empty:
            response = get_dataframe_list(df, DataFrameFields.FIELD_SYNONYMS.value)
            response = get_flat_list(response)
            return response
        return None
    

class SynonymSchema(ma.ModelSchema):
    class Meta:
        model = Synonym
