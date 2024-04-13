from gdo.core.GDT_Container import GDT_Container
from gdo.core.WithProxy import WithProxy
from gdo.ui.GDT_Paragraph import GDT_Paragraph
from gdo.ui.WithTitle import WithTitle


class GDT_Panel(WithProxy, WithTitle, GDT_Container):

    def __init__(self):
        super().__init__()

