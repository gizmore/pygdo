from functools import cmp_to_key

from gdo.base.GDO import GDO
from gdo.base.ResultArray import ResultArray
from gdo.table.GDT_Filter import GDT_Filter
from gdo.table.GDT_Order import GDT_Order
from gdo.table.GDT_PageNum import GDT_PageNum


class GDOSorter:

    @staticmethod
    def sort(result: list[GDO], order: GDT_Order) -> list[GDO]:
        sort_dict = order.get_order_dict()
        def compare(gdo1: GDO, gdo2: GDO):
            for key, direction in sort_dict.items():
                gdt = gdo1.column(key)
                cmp = gdt.gdo_compare(gdo1, gdo2)
                if direction == 'DESC':
                    cmp *= -1
                if cmp:
                    return cmp
            return 0  # Equal values

        return sorted(result, key=cmp_to_key(compare))

    @classmethod
    def filter(cls, result: list[GDO], filter: GDT_Filter) -> list[GDO]:
        vdict = filter.get_val()
        if not vdict: return result
        filtered: list[GDO] = []
        for gdo in result:
            ok = True
            for key, vals in vdict.items():
                hay = gdo.gdo_val(key) or ''
                if not any(val and val in hay for val in vals):
                    ok = False
                    break
            if ok:
                filtered.append(gdo)
        return filtered

    def paginate(cls, result: list[GDO], page: GDT_PageNum, ipp: int = 10) -> list[GDO]:
        begin = (page.get_value() - 1) * ipp
        return result[begin:begin+ipp]

    @classmethod
    def limit(cls, result: list[GDO], max_rows: int) -> list[GDO]:
        return result[0:max_rows]
