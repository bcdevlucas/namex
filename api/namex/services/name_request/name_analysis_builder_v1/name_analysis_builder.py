import itertools

import pandas as pd
from sqlalchemy import create_engine

from namex.services.name_request.auto_analyse.name_analysis_utils import build_query_distinctive, \
    build_query_descriptive, get_substitution_list, get_synonym_list, get_stop_word_list, get_en_designation_any_list, \
    get_en_designation_end_list, get_fr_designation_end_list, get_prefix_list, clean_name_words, get_classification, \
    data_frame_to_list, get_words_to_avoid, get_words_requiring_consent
from ..auto_analyse.abstract_name_analysis_builder \
    import AbstractNameAnalysisBuilder, ProcedureResult

from ..auto_analyse import AnalysisResultCodes, MAX_LIMIT

'''
Sample builder
# TODO: What convention should we use? Nice to use _v<BuilderVersion> if it doesn't break PEP8
'''


class NameAnalysisBuilder(AbstractNameAnalysisBuilder):
    # These properties are inherited from the parent
    # The build director (eg. NameAnalysisDirector) populates these properties
    # as part of its prepare_data
    # _synonyms = []
    # _substitutions = []
    # _stop_words = []
    # _designated_end_words = []
    # _designated_any_words = []
    #
    # _in_province_conflicts = []
    # _all_conflicts = []
    #
    # _name = ''

    _distinctive_words = []
    _descriptive_words = []

    POSTGRES_ADDRESS = 'localhost'
    POSTGRES_PORT = '5432'
    POSTGRES_USERNAME = 'postgres'
    POSTGRES_PASSWORD = 'BVict31C'
    POSTGRES_DBNAME_SYNS = 'local-sandbox-dev'
    POSTGRES_DBNAME_DATA = 'namex-local-dev'

    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=POSTGRES_USERNAME,
                                                                                            password=POSTGRES_PASSWORD,
                                                                                            ipaddress=POSTGRES_ADDRESS,
                                                                                            port=POSTGRES_PORT,
                                                                                            dbname=POSTGRES_DBNAME_DATA))

    cnx = create_engine(postgres_str)

    '''
    Check to see if a provided name is valid
    Override the abstract / base class method
    @return ProcedureResult
    '''

    def check_name_is_well_formed(self, list_desc, list_dist, list_none, name):

        result = ProcedureResult()
        result.is_valid = True

        # if (len(list_desc) > 0 and len(list_dist) > 0) and (list_desc != list_dist) and (
        #        (list_dist + list_desc) == name):
        #    success = True

        # Return one of the following:
        # AnalysisResultCodes.CONTAINS_UNCLASSIFIABLE_WORD
        # AnalysisResultCodes.TOO_MANY_WORDS
        # AnalysisResultCodes.ADD_DISTINCTIVE_WORD
        # AnalysisResultCodes.ADD_DESCRIPTIVE_WORD

        if len(list_none) > 0:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.CONTAINS_UNCLASSIFIABLE_WORD
        elif len(list_dist) < 1:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.ADD_DISTINCTIVE_WORD
        elif len(list_desc) < 1:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.ADD_DESCRIPTIVE_WORD
        elif len(name) > MAX_LIMIT:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.TOO_MANY_WORDS
        elif list_desc == list_dist:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.CONTAINS_UNCLASSIFIABLE_WORD
        elif list_dist + list_desc != name:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.CONTAINS_UNCLASSIFIABLE_WORD

        return result

    '''
    Override the abstract / base class method
    @return ProcedureResult
    '''

    def check_words_to_avoid(self, preprocessed_name):
        result = ProcedureResult()
        result.is_valid = True

        words_to_avoid_list = get_words_to_avoid()

        if any(words_to_avoid in preprocessed_name for words_to_avoid in words_to_avoid_list):
            result.is_valid = False
            result.result_code = AnalysisResultCodes.WORD_TO_AVOID

        return result

    '''
    Override the abstract / base class method
    Input: list_dist= ['MOUNTAIN', 'VIEW']
           list_desc= ['FOOD', 'GROWERS']
    @return ProcedureResult
    '''

    def search_conflicts(self, list_dist, list_desc, cnx=create_engine(postgres_str)):
        result = ProcedureResult()
        result.is_valid = False

        # dist_substitution_list:  [['mount', 'mountain', 'mt', 'mtn'], ['view', 'vu']]
        # desc_substitution_list: [['food, restaurant, bar'],['growers']]

        distinctive = ' '.join(map(str, list_dist)).replace(',', ' ').upper().strip()

        dist_substitution_list = []

        for w_dist in list_dist:
            substitution_list = get_substitution_list(w_dist)
            if substitution_list:
                dist_substitution_list.append(substitution_list)
            else:
                dist_substitution_list.append(w_dist.lower())

        # All possible permutations of elements in dist_list
        # [('mount', 'view'), ('mount', 'vu'), ('mountain', 'view'), ('mountain', 'vu'), ('mt', 'view'), ('mt', 'vu'), ('mtn', 'view'),
        #  ('mtn', 'vu')]
        if dist_substitution_list:
            dist_all_permutations = list(itertools.product(*dist_substitution_list))
            query = build_query_distinctive(dist_all_permutations)

            desc_synonym_list = []
            for w_desc in list_desc:
                synonym_list = get_synonym_list(w_desc)
                if synonym_list:
                    desc_synonym_list.extend(synonym_list)
                else:
                    desc_synonym_list.extend([w_desc.lower()])

            if desc_synonym_list:
                query = build_query_descriptive(desc_synonym_list, query)
                matches = pd.read_sql_query(query, cnx)

                if matches.values.tolist():
                    result.is_valid = False
                    result.result_code = AnalysisResultCodes.CORPORATE_CONFLICT
                else:
                    result.is_valid = True
                    result.result_code = AnalysisResultCodes.VALID_NAME
            else:
                result.is_valid = False
                result.result_code = AnalysisResultCodes.ADD_DESCRIPTIVE_WORD
        else:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.ADD_DISTINCTIVE_WORD

        return result

    '''
    Override the abstract / base class method
    @return ProcedureResult
    '''

    def check_words_requiring_consent(self, preprocessed_name):
        result = ProcedureResult()
        result.is_valid = True

        words_consent_list= get_words_requiring_consent()

        if any(words_consent in preprocessed_name for words_consent in words_consent_list):
            result.is_valid = False
            result.result_code = AnalysisResultCodes.NAME_REQUIRES_CONSENT

        return result

    '''
    Override the abstract / base class method
    @return ProcedureResult
    '''

    def check_designation(self):
        result = ProcedureResult()
        result.is_valid = True

        if not result.is_valid:
            result.is_valid = False
            result.result_code = AnalysisResultCodes.DESIGNATION_MISMATCH

        return result

    '''
    Override the abstract / base class method
    @return ProcedureResult
    '''

    def do_analysis(self, name):
        result = ProcedureResult()
        result.is_valid = False

        stop_words = get_stop_word_list()
        en_designation_any = get_en_designation_any_list()
        en_designation_end = get_en_designation_end_list()
        fr_designation_end = get_fr_designation_end_list()
        prefixes = get_prefix_list()
        cf = pd.DataFrame(columns=['word', 'word_classification'])

        preprocessed_name_list = clean_name_words(name, stop_words, en_designation_any, en_designation_end,
                                                  fr_designation_end, prefixes)

        for word in preprocessed_name_list:
            classification = get_classification(word)
            new_row = {'word': word.lower().strip(), 'word_classification': classification.strip()}
            cf = cf.append(new_row, ignore_index=True)

        distinctive_list, descriptive_list, unclassified_list = data_frame_to_list(cf)

        well_formed = self.check_name_is_well_formed(descriptive_list, distinctive_list, unclassified_list, \
                                                     preprocessed_name_list)
        if well_formed.is_valid:
            preprocessed_name = ' '.join(map(str, preprocessed_name_list))
            check_words_to_avoid = self.check_words_to_avoid(preprocessed_name)
            check_conflicts = self.search_conflicts(distinctive_list, descriptive_list)

            if not check_conflicts:

                check_words_requiring_consent = self.check_words_requiring_consent(preprocessed_name)

                # check_designation_mismatch = self.check_designation()
                '''
                if not check_name_is_well_formed.is_valid:
                    return check_name_is_well_formed
        
                if not check_words_to_avoid.is_valid:
                    return check_words_to_avoid
        
                if not check_conflicts.is_valid:
                    return check_conflicts
        
                if not check_words_requiring_consent.is_valid:
                    return check_words_requiring_consent
        
                if not check_designation_mismatch.is_valid:
                    return check_designation_mismatch
                '''
            else:
                return result
        else:
            return result

            return ProcedureResult(is_valid=True)
