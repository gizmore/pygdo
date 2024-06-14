from gdo.base.GDT import GDT


class GDT_Composite(GDT):
    """
    A composite GDT for multiple database columns.
    """

    def gdo_components(self) -> list[GDT]:
        return []
