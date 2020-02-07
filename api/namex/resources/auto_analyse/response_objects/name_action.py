from . import Serializable

from enum import Enum


class NameActions(Enum):
    STRIKE = 'strike'
    HIGHLIGHT = 'highlight'
    BRACKETS = 'brackets'
    SPELLING = 'spelling'

    @classmethod
    def list(cls):
        values = []
        for item in cls:
            values.append(item.value)

        return values


class WordPositions(Enum):
    START = 'start'
    END = 'end'

    @classmethod
    def list(cls):
        values = []
        for item in cls:
            values.append(item.value)

        return values


class NameAction(Serializable):
    def __init__(self, **kwargs):
        # Required!
        if not kwargs.get('type').value in NameActions.list():
            raise TypeError('Invalid NameAction')

        if kwargs.get('position') and kwargs['position'].value not in WordPositions.list():
            raise TypeError('Invalid word position')

        # TODO: Make sure index is valid! Add validation.

        self.type = kwargs['type'].value
        self.index = kwargs['index'].value if kwargs.get('index') else None
        self.position = kwargs['position'].value if kwargs.get('position') else None  # [start | end] (is there another?)
        self.message = kwargs['message'] if kwargs.get('message') else None  # <string> | None
