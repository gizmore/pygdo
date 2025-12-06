from gdo.core.GDT_UInt import GDT_UInt


class GDT_PageNum(GDT_UInt):

    @classmethod
    def get_page_num(cls, item_num: int, ipp: int):
        return (item_num + 1) // ipp
