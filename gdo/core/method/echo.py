from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String


class echo(Method):

    def cli_trigger(self) -> str:
        return 'echo'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_RestOfText('text').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        text = self.param_value('text')
        return GDT_String('response').initial(text)
