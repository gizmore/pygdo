from functools import cmp_to_key

from gdo.base.GDO import GDO
from gdo.base.ResultArray import ResultArray
from gdo.table.GDT_Order import GDT_Order


class GDOSorter:

    @staticmethod
    def sort(result: ResultArray, order: GDT_Order) -> list[GDO]:
        sort_dict = order.get_order_dict()
        def compare(gdo1: GDO, gdo2: GDO):
            for key, direction in sort_dict.items():
                cmp = gdo1.column(key).gdo_compare(gdo2.column(key))
                if direction.lower() == 'desc':
                    cmp = cmp * -1
                if cmp:
                    return cmp
            return 0  # Equal values

        return sorted(result._data, key=cmp_to_key(compare))
