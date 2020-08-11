from namex.models import db, State, Request as RequestDAO, Name as NameDAO

default_test_names = [
    {
        'name': 'ABC ENGINEERING',
        "choice": 1,
        "designation": "LTD.",
        "name_type_cd": "CO",
        "consent_words": "",
        "conflict1": "ABC ENGINEERING LTD.",
        "conflict1_num": "0515211"
    },
    {
        'name': 'ABC PLUMBING',
        "choice": 1,
        "designation": "LTD.",
        "name_type_cd": "CO",
        "consent_words": "",
        "conflict1": "ABC PLUMBING LTD.",
        "conflict1_num": "0515211"
    }
]


def build_name(test_name):
    name = NameDAO()
    # TODO: Why are these sequences NOT auto increment, why do we have to update the seq manually?
    # name.id = test_name.get('id', None)
    seq = db.Sequence('names_id_seq')
    name_id = db.engine.execute(seq)
    name.id = test_name.get('id', name_id)
    name.choice = 1
    name.name = test_name.get('name', '')
    name.designation = test_name.get('designation', '')
    name.name_type_cd = test_name.get('name_type_cd', '')
    name.consent_words = test_name.get('consent_words', '')
    name.conflict1 = test_name.get('conflict1', '')
    name.conflict1_num = test_name.get('conflict1_num', '')

    return name


def build_nr(nr_state, data=None, test_names=None):
    """
    Creates an NR in a given state.
    :param nr_state:
    :param data:
    :param test_names:
    :return:
    """
    test_names = test_names if test_names else default_test_names

    return {
        State.DRAFT: build_draft,
        State.RESERVED: build_reserved,
        State.COND_RESERVE: build_cond_reserved,
        State.CONDITIONAL: build_conditional,
        State.APPROVED: build_approved
    }.get(nr_state)(data, test_names)


def build_draft(data=None, test_names=None):
    nr = RequestDAO()

    # Set defaults, if these exist in the provided data they will be overwritten
    nr.stateCd = State.DRAFT
    nr.requestId = 1460775
    nr._source = 'NRO'

    if not data:
        data = {}

    # Map the data, if provided
    for key, value in data.items():
        nr.__setattr__(key, value)

    nr.names = []
    for test_name in test_names:
        nr.names.append(build_name(test_name))

    return nr


def build_cond_reserved(data=None, test_names=None):
    nr = RequestDAO()

    # Set defaults, if these exist in the provided data they will be overwritten
    nr.stateCd = State.COND_RESERVE
    nr.requestId = 1460775
    nr._source = 'NRO'

    if not data:
        data = {}

    # Map the data, if provided
    for key, value in data.items():
        nr.__setattr__(key, value)

    nr.names = []
    for test_name in test_names:
        nr.names.append(build_name(test_name))

    return nr


def build_reserved(data=None, test_names=None):
    nr = RequestDAO()

    # Set defaults, if these exist in the provided data they will be overwritten
    nr.stateCd = State.RESERVED
    nr.requestId = 1460775
    nr._source = 'NRO'

    if not data:
        data = {}

    # Map the data, if provided
    for key, value in data.items():
        nr.__setattr__(key, value)

    nr.names = []
    for test_name in test_names:
        nr.names.append(build_name(test_name))

    return nr


def build_conditional(data=None, test_names=None):
    nr = RequestDAO()

    # Set defaults, if these exist in the provided data they will be overwritten
    nr.stateCd = State.CONDITIONAL
    nr.requestId = 1460775
    nr._source = 'NRO'

    if not data:
        data = {}

    # Map the data, if provided
    for key, value in data.items():
        nr.__setattr__(key, value)

    nr.names = []
    for test_name in test_names:
        nr.names.append(build_name(test_name))

    return nr


def build_approved(data=None, test_names=None):
    nr = RequestDAO()

    # Set defaults, if these exist in the provided data they will be overwritten
    nr.stateCd = State.APPROVED
    nr.requestId = 1460775
    nr._source = 'NRO'

    if not data:
        data = {}

    # Map the data, if provided
    for key, value in data.items():
        nr.__setattr__(key, value)

    nr.names = []
    for test_name in test_names:
        nr.names.append(build_name(test_name))

    return nr
