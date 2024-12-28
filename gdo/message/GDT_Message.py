from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.GDT_Composite import GDT_Composite
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import GDT_Template
from gdo.core.GDT_Text import GDT_Text
from gdo.message.GDT_Editor import GDT_Editor


class GDT_Message(GDT_Composite, GDT_Field):

    def __init__(self, name):
        super().__init__(name)

    def gdo_components(self) -> list['GDT']:
        components = []
        components.append(GDT_Editor(f"{self._name}_editor"))
        components.append(GDT_Text(f"{self._name}_input"))
        components.append(GDT_Text(f"{self._name}_plain"))
        for mode in Mode.explicit():
            components.append(GDT_Text(f"{self._name}_{mode.name.lower()}"))
        return [
        ]

    def render_form(self):
        return GDT_Template.python('ui', 'form_message.html', {"field": self})

