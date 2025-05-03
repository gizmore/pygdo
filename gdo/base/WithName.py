class WithName:

    _name: str

    def name(self, name: str):
        self._name = name
        return self

    def generate_name(self):
        return f'{self.__class__.__name__}#{id(self)}'

    def get_name(self):
        return self._name

