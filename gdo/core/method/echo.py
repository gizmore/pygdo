from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText


class echo(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_RestOfText('text').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        text = self.param_value('text')
        return self.message_raw(text)

