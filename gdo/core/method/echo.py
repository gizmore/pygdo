from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String


class echo(Method):

    def gdo_trigger(self) -> str:
        return 'echo'

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_String('sep').initial(' '),
            GDT_RestOfText('text').not_null(),
        ]

    def get_separator(self) -> str:
        return self.param_val('sep') or ''  # Can be null

    def gdo_execute(self) -> GDT:
        sep = self.get_separator()
        return GDT_String('text').val(sep.join(self.param_value('text')))
