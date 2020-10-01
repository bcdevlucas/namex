from namex.models import State

# Only allow editing if the request is in certain valid states
request_editable_states = [
    State.DRAFT,
    State.RESERVED,
    State.COND_RESERVE
]

contact_editable_states = [
    State.APPROVED,
    State.REJECTED,
    State.CONDITIONAL
]
