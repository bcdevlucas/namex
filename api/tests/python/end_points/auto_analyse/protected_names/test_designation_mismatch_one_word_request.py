import pytest
import jsonpickle

from urllib.parse import quote_plus

from namex.services.name_request.auto_analyse import AnalysisIssueCodes

from ..common import assert_issues_count_is_gt, assert_has_word_upper, assert_has_designations_upper, \
    save_words_list_classification, save_words_list_virtual_word_condition
from ..common import ENDPOINT_PATH
from ..common import token_header, claims


# TODO: COOP is also a special word. What if coop is typed in CR entity type. Do we show mismatch designation and special word use?
@pytest.mark.xfail(raises=ValueError)
def test_designation_mismatch_one_word_request_response(client, jwt, app):
    words_list_classification = [{'word': 'ARMSTRONG', 'classification': 'DIST'},
                                 {'word': 'ARMSTRONG', 'classification': 'DESC'},
                                 {'word': 'PLUMBING', 'classification': 'DIST'},
                                 {'word': 'PLUMBING', 'classification': 'DESC'},
                                 {'word': 'BC', 'classification': 'DIST'},
                                 {'word': 'BC', 'classification': 'DESC'}
                                 ]
    save_words_list_classification(words_list_classification)

    words_list_virtual_word_condition = [
        {
            'words': 'B C, B C S, BC, BC S, BCPROVINCE, BRITISH COLUMBIA, BRITISHCOLUMBIA, PROVINCIAL',
            'consent_required': False, 'allow_use': True
        },
        {
            'words': 'CO OP, CO OPERATIVES, COOP, COOPERATIVES',
            'consent_required': False, 'allow_use': True
        }
    ]
    save_words_list_virtual_word_condition(words_list_virtual_word_condition)
    # create JWT & setup header with a Bearer Token using the JWT
    token = jwt.create_jwt(claims, token_header)
    headers = {'Authorization': 'Bearer ' + token, 'content-type': 'application/json'}

    test_params = [
        {
            'name': 'ARMSTRONG PLUMBING COOP',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING COOPERATIVE',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': '468040 BC COOP',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING LLC',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG LLC PLUMBING',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING LLP',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING SLR',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING SENCRL',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING CCC',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG PLUMBING ULC',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        },
        {
            'name': 'ARMSTRONG LTD PLUMBING',
            'location': 'BC',
            'entity_type': 'CR',
            'request_action': 'NEW'
        }
    ]

    for entry in test_params:
        query = '&'.join("{!s}={}".format(k, quote_plus(v)) for (k, v) in entry.items())
        path = ENDPOINT_PATH + '?' + query
        print('\n' + 'request: ' + path + '\n')
        response = client.get(path, headers=headers)
        payload = jsonpickle.decode(response.data)
        print("Assert that the payload contains issues")
        if isinstance(payload.get('issues'), list):
            assert_issues_count_is_gt(0, payload.get('issues'))
            assert_has_word_upper(AnalysisIssueCodes.DESIGNATION_MISMATCH, payload.get('issues'))
            assert_has_designations_upper(AnalysisIssueCodes.DESIGNATION_MISMATCH, payload.get('issues'))
