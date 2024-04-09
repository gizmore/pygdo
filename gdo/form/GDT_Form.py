from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Field import GDT_Field
from gdo.ui.GDT_Title import GDT_Title


class GDT_Form(GDT_Field,GDT_Container):

    _title: GDT_Title
    _info: GDT_Paragraph

    def __init__(self):
        super().__init__()

