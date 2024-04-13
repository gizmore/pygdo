from gdo.core.GDT_String import GDT_String
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Error(GDT_Panel):

    def __init__(self):
        super().__init__()
        self.proxy(GDT_String)
        