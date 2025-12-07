from gdo.core.GDT_String import GDT_String


class GDT_Secret(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('password')
        self._input_type = 'password'

    def is_secret(self) -> bool:
        return True
