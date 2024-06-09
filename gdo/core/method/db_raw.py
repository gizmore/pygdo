from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText


class db_raw(Method):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_RestOfText('sql').not_null(),
        ]

    def gdo_execute(self):
        pass

