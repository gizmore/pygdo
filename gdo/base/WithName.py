from gdo.base.GDT import GDT


class WithName:
    _name: str

    def name(self, name: str):
        self._name = name
        return self

    def generate_name(self):
        return self.__class__.__name__ + "#" + str(GDT.GDT_COUNT)

    def get_name(self):
        return self._name

