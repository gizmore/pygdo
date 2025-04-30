from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String


class echo(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'echo'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_RestOfText('text').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        text = self.param_value('text')
        return GDT_String('text').val(text)
