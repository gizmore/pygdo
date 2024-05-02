import htmlpurifier

from gdo.core.GDT_Template import GDT_Template
from gdo.core.GDT_Text import GDT_Text


class GDT_Message(GDT_Text):

    def __init__(self, name):
        super().__init__(name)

    def render_form(self):
        GDT_Template.python('ui', 'form_message.html', {"field": self})

