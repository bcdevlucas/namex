from namex.models import Synonym

from .mixins.get_synonyms_lists import GetSynonymsListsMixin
from .mixins.get_designations_lists import GetDesignationsListsMixin
from .mixins.get_word_classification_lists import GetWordClassificationListsMixin

from . import AnalysisResultCodes

from namex.services.synonyms.synonym \
    import SynonymService

from namex.services.name_processing.name_processing \
    import NameProcessingService

from namex.services.word_classification.word_classification \
    import WordClassificationService

from namex.services.word_classification.token_classifier \
    import TokenClassifier

from namex.services.virtual_word_condition.virtual_word_condition \
    import VirtualWordConditionService

'''
This is the director for AutoAnalyseService.
'''


class NameAnalysisDirector(GetSynonymsListsMixin, GetDesignationsListsMixin, GetWordClassificationListsMixin):
    @property
    def word_classification_service(self):
        return self._word_classification_service

    @word_classification_service.setter
    def word_classification_service(self, svc):
        self._word_classification_service = svc

    @property
    def word_condition_service(self):
        return self._word_condition_service

    @word_condition_service.setter
    def word_condition_service(self, svc):
        self._word_condition_service = svc

    @property
    def synonym_service(self):
        return self._synonym_service

    @synonym_service.setter
    def synonym_service(self, svc):
        self._synonym_service = svc

    @property
    def name_processing_service(self):
        return self._name_processing_service

    @name_processing_service.setter
    def name_processing_service(self, svc):
        self._name_processing_service = svc

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder):
        self._builder = builder

    @property
    def model(self):
        return Synonym

    @property
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        self._entity_type = entity_type

    @property
    def name_tokens(self):
        np_svc = self.name_processing_service
        return self.name_processing_service.name_tokens if np_svc else ''

    @property
    def token_classifier(self):
        return self._token_classifier

    @token_classifier.setter
    def token_classifier(self, token_classifier):
        self._token_classifier = token_classifier

    @property
    def word_classification_tokens(self):
        return \
            self.token_classifier.distinctive_word_tokens, \
            self.token_classifier.descriptive_word_tokens, \
            self.token_classifier.unclassified_word_tokens

    @property
    def processed_name(self):
        np_svc = self.name_processing_service
        return self.name_processing_service.processed_name if np_svc else ''

    @property
    def name_as_submitted(self):
        np_svc = self.name_processing_service
        return self.name_processing_service.name_as_submitted if np_svc else ''

    '''
    Just an alias for name_as_submitted
    '''
    @property
    def original_name(self):
        return self.name_as_submitted

    def __init__(self):
        self.synonym_service = SynonymService()
        self.word_classification_service = WordClassificationService()
        self.word_condition_service = VirtualWordConditionService()
        self.name_processing_service = NameProcessingService()

        self.builder = None
        self.token_classifier = None

        self.entity_type = None

    # Call this method from whatever is using this director
    def use_builder(self, builder):
        self.builder = builder if builder else None

    # Convenience method for extending implementations
    def get_entity_type(self):
        return self.entity_type

    # Convenience method for extending implementations
    def set_entity_type(self, entity_type):
        self.entity_type = entity_type

    # API for extending implementations
    def get_name_tokens(self):
        return self.name_tokens

    # API for extending implementations
    # TODO: Just for backward compat. et rid of this when we are done refactoring!
    def get_name(self):
        return self.name_tokens

    # API for extending implementations
    def get_original_name(self):
        return self.original_name

    # API for extending implementations
    def get_processed_name(self):
        return self.processed_name

    '''
    Set and preprocess a submitted name string.
    Setting the name using np_svc.set_name will clean the name and set the following properties:
    @:prop name_as_submitted The original name string
    @:prop processed_name The cleaned name
    @:prop name_tokens Word tokens generated from the cleaned name
    '''
    def set_name(self, name):
        np_svc = self.name_processing_service
        wc_svc = self.word_classification_service

        np_svc.set_name(name)

        # TODO: Get rid of this when done refactoring!
        self._list_name_words = np_svc.name_tokens

        # Classify the tokens that were created by NameProcessingService
        self.token_classifier = wc_svc.classify_tokens(np_svc.name_tokens)

        self.configure_builder()

    '''
    Prepare any data required by the analysis builder.
    prepare_data is an abstract method and must be implemented in extending classes.
    '''
    def prepare_data(self):
        # Query for whatever data we need to load up here
        self.configure_builder()

    def configure_builder(self):
        # Do anything else required to configure the builder
        pass

    '''
    This is the main execution call that wraps name analysis checks. 
    - Perform checks to ensure the name is well formed. 
    - If the name is well formed, proceed with our analysis by calling do_analysis.
    - If you don't want to check to see if a name is well formed first, override check_name_is_well_formed in the supplied builder.
    @:return ProcedureResult[]
    '''
    def execute_analysis(self):
        try:
            # Execute analysis using the supplied builder
            builder = self.builder

            list_name = self.name_tokens
            list_dist, list_desc, list_none = self.word_classification_tokens

            results = []
            if list_none and list_none.__len__() > 0:
                self._list_dist_words, self._list_desc_words = TokenClassifier.handle_unclassified_words(
                    list_dist,
                    list_desc,
                    list_none,
                    list_name
                )

            check_name_is_well_formed = builder.check_name_is_well_formed(
                self.token_classifier.distinctive_word_tokens,
                self.token_classifier.descriptive_word_tokens,
                self.token_classifier.unclassified_word_tokens,
                self.name_tokens
            )

            results = results + check_name_is_well_formed
            # If the error coming back is that a name is not well formed
            # eg. result.result_code = AnalysisResultCodes.CONTAINS_UNCLASSIFIABLE_WORD
            # don't return the result yet, the name is well formed, we just have an unclassified
            # word in the result.

            issues_that_must_be_fixed = [
                AnalysisResultCodes.ADD_DISTINCTIVE_WORD,
                AnalysisResultCodes.ADD_DESCRIPTIVE_WORD,
                AnalysisResultCodes.TOO_MANY_WORDS
            ]

            issue_must_be_fixed = False
            result_codes = list(map(lambda r: r.result_code, results))

            for code in result_codes:
                if code in issues_that_must_be_fixed:
                    issue_must_be_fixed = True
                    break

            if issue_must_be_fixed:
                return results

                #  Name is not well formed - do not continue

            analysis = results + self.do_analysis()

            if not analysis:
                # TODO: Get the classname of the concrete class, somehow, for the message...
                raise ValueError('NameAnalysisDirector.execute_analysis did not return a result')

            return analysis

        except Exception as error:
            print('Error executing name analysis: ' + repr(error))

    '''
    This is the main execution call for running name analysis checks.
    do_analysis is an abstract method and must be implemented in extending classes.
    @:return ProcedureResult[]
    '''
    def do_analysis(self):
        raise NotImplementedError('do_analysis must be implemented in extending classes')
