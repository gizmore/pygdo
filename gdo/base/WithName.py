

class WithName:
    _name: str

    def name(self, name: str):
        self._name = name
        return self

    def get_name(self):
        return self._name

