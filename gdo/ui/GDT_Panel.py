from gdo.base.GDT import GDT
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Panel(WithTitle, WithText, GDT):

    def __init__(self):
        super().__init__()

