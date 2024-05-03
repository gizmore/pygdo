import functools

from gdo.base.GDT import GDT
from gdo.base.Method import Method


class MethodTable(Method):
    def __init__(self):
        super().__init__()

    @functools.cache
    def table_parameters(self) -> list[GDT]:
        params = []
        if self.gdo_paginated():
            params.append(GDT_Page(self.gdo_paginate_name()))

        return params


    ############
    # Abstract #
    ############

    def gdo_sorted(self) -> bool:
        return True

    def gdo_ordered(self) -> bool:
        return True

    def gdo_searched(self) -> bool:
        return True

    def gdo_paginated(self) -> bool:
        return True

    def gdo_paginate_name(self) -> str:
        return 'p'

    ########
    # Exec #
    ########
    def gdo_execute(self):

