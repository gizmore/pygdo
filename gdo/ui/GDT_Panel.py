from gdo.core.GDT_Container import GDT_Container
from gdo.ui.GDT_Title import GDT_Title


class GDT_Panel(GDT_Container):
    _title: GDT_Title

    def __init__(self):
        super().__init__()
