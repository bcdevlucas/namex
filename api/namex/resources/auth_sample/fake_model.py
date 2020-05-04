class FakeModel:
    data = [
        {'id': 1, 'name': 'Bob Johnson'},
        {'id': 2, 'name': 'George Michael'},
        {'id': 3, 'name': 'Ryan Fitzpatrick'},
    ]

    @classmethod
    def get_entity_by_id(cls, entity_id):
        matches = list(filter(lambda x: x['id'] == int(entity_id), cls.data))
        if len(matches) > 0:
            return matches[0]

        return None

    @classmethod
    def find(cls):
        return cls.data

    @classmethod
    def create(cls, entity):
        return entity

    @classmethod
    def update(cls, entity_id):
        matches = list(filter(lambda x: x['id'] == int(entity_id), cls.data))
        if len(matches) > 0:
            return matches[0]

        return None

    @classmethod
    def delete(cls):
        return True
