import functools
from typing import Iterator

from gdo.base.Exceptions import GDOException
from gdo.base.GDO import GDO
from gdo.base.GDOSorter import GDOSorter
from gdo.base.GDT import GDT
from gdo.base.Render import Mode, Render
from gdo.base.Result import Result
from gdo.base.ResultArray import ResultArray
from gdo.core.WithGDO import WithGDO
from gdo.form.MethodForm import MethodForm
from gdo.table.module_table import module_table
from gdo.table.GDT_Filter import GDT_Filter
from gdo.table.GDT_Order import GDT_Order
from gdo.table.GDT_PageNum import GDT_PageNum
from gdo.table.GDT_Search import GDT_Search
from gdo.table.GDT_Table import GDT_Table, TableMode


class MethodTable(WithGDO, MethodForm):
    """
    A method that displays a table.
    """

    _curr_table_row_id: int

    def __init__(self):
        super().__init__()
        self._curr_table_row_id = 0

    def parameters(self, reset: bool = False) -> dict[str,GDT]:
        if hasattr(self, '_parameters') and not reset:
            return self._parameters
        params = super().parameters(reset)
        tp = self.table_parameters()
        for gdt in tp:
            params[gdt.get_name()] = gdt
        self.set_parameter_positions()
        for gdt in tp:
            self.init_parameter(gdt)
        return params

    ################
    # Table Params #
    ################

    @functools.cache
    def table_parameters(self) -> Iterator[GDT]:
        if self.gdo_paginated():
            yield GDT_PageNum(self.gdo_paginate_name()).initial('1').positional(self.gdo_page_positional())
        if self.gdo_ordered():
            yield GDT_Order(self.gdo_order_name())
        if self.gdo_filtered():
            yield GDT_Filter(self.gdo_filter_name())
        if self.gdo_searched():
            yield GDT_Search(self.gdo_search_name()).label('search').positional(self.gdo_search_positional())

    def table_order_field(self) -> GDT_Order:
        return self.parameter(self.gdo_order_name())

    def table_filter_field(self) -> GDT_Order:
        return self.parameter(self.gdo_filter_name())

    def table_search_field(self) -> GDT_Search:
        return self.parameter(self.gdo_search_name())

    def table_paginate_field(self) -> GDT_PageNum:
        return self.parameter(self.gdo_paginate_name())

    ##################
    # Abstract table #
    ##################

    def gdo_table(self) -> GDO:
        raise GDOException(f"{self.__class__.__name__} does not implement gdo_table()")

    def gdo_table_mode(self) -> TableMode:
        return TableMode.TABLE

    def gdo_table_headers(self) -> list[GDT]:
        return list(filter(lambda gdt: not gdt.is_hidden(), self.gdo_table().columns().values()))

    def gdo_table_result(self) -> Result:
        raise GDOException(f"{self.__class__.__name__} does not implement gdo_table_result()")

    def get_num_results(self) -> int:
        return self.gdo_table_result().get_num_rows()

    ##################
    # Abstract hooks #
    ##################
    def gdo_create_table(self, table: GDT_Table):
        pass

    #####################
    # Abstract Features #
    #####################

    def gdo_max_results(self) -> int:
        return 200

    def gdo_page_positional(self) -> bool:
        return True

    def gdo_paginated(self) -> bool:
        return True

    def get_page_num(self) -> int:
        return self.param_value(self.gdo_paginate_name())

    def get_num_pages(self) -> int:
        return ((self.get_num_results()-1) // self.gdo_paginate_size()) + 1

    def gdo_paginate_size(self) -> int:
        return module_table.instance().cfg_ipp()

    def gdo_paginate_name(self) -> str:
        return 'page'

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

    def gdo_search_positional(self) -> bool:
        return False

    def gdo_search_name(self) -> str:
        return 's'

    #########
    # Table #
    #########
    @functools.cache
    def get_table(self) -> GDT_Table:
        self.init_parameters()
        table = GDT_Table()
        table.method(self)
        self.gdo_create_table(table)
        return table

    def get_table_result(self) -> Result:
        result = self.gdo_table_result()._data
        if self.gdo_ordered():
            result = GDOSorter.sort(result, self.parameter(self.gdo_order_name()))
        if self.gdo_filtered():
            result = GDOSorter.filter(result, self.parameter(self.gdo_filter_name()))
        if self.gdo_paginated():
            result = GDOSorter.paginate(result, self.parameter(self.gdo_paginate_name()), self.gdo_paginate_size())
        elif max := self.gdo_max_results():
            result = GDOSorter.limit(result, max)
        return result

    ########
    # Exec #
    ########
    def gdo_execute(self) -> GDT:
        # self.init_parameters(False)
        table = self.get_table()
        table.mode(self.gdo_table_mode())
        if self.gdo_paginated():
            self._curr_table_row_id = self.gdo_paginate_size() * (self.table_paginate_field().get_value() - 1)
        else:
            self._curr_table_row_id = 0
        return table

    ##########
    # Render #
    ##########
    def render(self, mode: Mode = Mode.HTML):
        return self.get_table().render(mode)

    def render_gdo(self, gdo: GDO, mode: Mode) -> any:
        if mode == Mode.JSON:
            return { gdt.get_name(): gdt.gdo(gdo).render_json() for gdt in self.gdo_table_headers()}
        self._curr_table_row_id += 1
        return f"{Render.bold(str(self._curr_table_row_id), mode)}-{gdo.render_name()}"

    def render_page(self) -> GDT:
        return self.get_table()
