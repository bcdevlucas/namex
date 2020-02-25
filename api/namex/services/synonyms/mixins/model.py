from . import SynonymServiceMixin

"""
Model accessors for the Synonym service.
"""


class SynonymModelMixin(SynonymServiceMixin):
    def get_query_distinctive(self, dist_all_permutations, length):
        query = self._model.build_query_distinctive(dist_all_permutations, length)
        return query

    def get_query_descriptive(self, desc_substitution_list,query):
        query = self._model.build_query_descriptive(desc_substitution_list, query)
        return query

    def get_synonym_list(self, word):
        synonym_list = self._model.get_synonym_list(word)
        return synonym_list

    def get_substitution_list(self, word):
        substitution_list = self._model.get_substitution_list(word)
        return substitution_list

    def get_all_substitutions_synonyms(self, list_d, distinctive=True):
        aux_list = []
        response_list = []

        for word in list_d:
            if distinctive:
                aux_list = self.get_substitution_list(word)
            else:
                aux_list = self.get_synonym_list(word)
            if aux_list:
                response_list.append(aux_list)
            else:
                response_list.append([word.lower()])

        return response_list

    def get_conflicts(self, query):
        conflicts = self._model.get_conflicts(query)
        return conflicts


