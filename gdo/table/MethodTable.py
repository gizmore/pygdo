import functools

from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Result import Result
from gdo.base.ResultArray import ResultArray
from gdo.core.WithGDO import WithGDO
from gdo.form.MethodForm import MethodForm
from gdo.table.GDT_Filter import GDT_Filter
from gdo.table.GDT_Order import GDT_Order
from gdo.table.GDT_PageNum import GDT_PageNum
from gdo.table.GDT_Search import GDT_Search
from gdo.table.GDT_Table import GDT_Table, TableMode


class MethodTable(WithGDO, MethodForm):
    """
    A method that displays a table.
    """

    def __init__(self):
        super().__init__()

    def parameters(self, reset: bool = False) -> dict[str, GDT]:
        params = super().parameters()
        for gdt in self.table_parameters():
            params[gdt.get_name()] = gdt
        return params

    ################
    # Table Params #
    ################

    @functools.cache
    def table_parameters(self) -> list[GDT]:
        params = []
        if self.gdo_paginated():
            params.append(GDT_PageNum(self.gdo_paginate_name()))
        if self.gdo_ordered():
            params.append(GDT_Order(self.gdo_order_name()))
        if self.gdo_filtered():
            params.append(GDT_Filter(self.gdo_filter_name()))
        if self.gdo_searched():
            params.append(GDT_Search(self.gdo_search_name()))
        return params

    def table_order_field(self) -> GDT_Order:
        return self.parameter(self.gdo_order_name())

    def table_filter_field(self) -> GDT_Order:
        return self.parameter(self.gdo_filter_name())

    def table_search_field(self) -> GDT_Search:
        return self.parameter(self.gdo_search_name())

    ##################
    # Abstract table #
    ##################

    def gdo_table(self) -> GDO:
        pass

    def gdo_table_mode(self) -> TableMode:
        return TableMode.TABLE

    def gdo_table_headers(self) -> list[GDT]:
        return list(filter(lambda gdt: not gdt.is_hidden(), self.gdo_table().columns()))

    def gdo_table_result(self) -> Result:
        return ResultArray([], self.gdo_table())

    ##################
    # Abstract hooks #
    ##################
    def gdo_create_table(self, table: GDT_Table):
        pass

    #####################
    # Abstract Features #
    #####################

    def gdo_paginated(self) -> bool:
        return True

    def gdo_paginate_name(self) -> str:
        return 'p'

    def gdo_ordered(self) -> bool:
        return True

    def gdo_order_name(self) -> str:
        return 'o'

    def gdo_order_default(self):
        for gdt in self.gdo_table_headers():
            if gdt.is_orderable():
                return f"{gdt.get_name()} {gdt.default_order()}"

    def gdo_filtered(self) -> bool:
        return True

    def gdo_filter_name(self) -> str:
        return 'f'

    def gdo_searched(self) -> bool:
        return True

    def gdo_search_name(self) -> str:
        return 's'

    #########
    # Table #
    #########
    @functools.cache
    def get_table(self):
        table = GDT_Table()
        table.method(self)
        self.gdo_create_table(table)
        return table

    ########
    # Exec #
    ########
    def gdo_execute(self):
        table = self.get_table()
        table.mode(self.gdo_table_mode())
        return table

    ##########
    # Render #
    ##########
    def render(self, mode: Mode = Mode.HTML):
        return self.render_gdt(mode)
