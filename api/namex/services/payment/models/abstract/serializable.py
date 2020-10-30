import jsonpickle


class Serializable(dict):
    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.casefold()
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.casefold()
        return super().__getitem__(key)

    def to_json_test(self):
        # Allows us to unwrap the response when we're running pytests
        return jsonpickle.encode(self)

    def to_json(self):
        return jsonpickle.encode(self, unpicklable=False, warn=True)
