from functools import lru_cache

from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.GDT_Composite import GDT_Composite
from gdo.core.GDT_Template import GDT_Template
from gdo.core.GDT_Text import GDT_Text
from gdo.message.editor.Editor import Editor
from gdo.message.editor.GDT_Editor import GDT_Editor


class GDT_Message(GDT_Composite, GDT_Text):

    def __init__(self, name: str):
        super().__init__(name)
        self.label(name)

    @lru_cache
    def gdo_components(self) -> list['GDT']:
        components = [
            GDT_Editor(f"{self._name}_editor").not_null(),
        ]
        for mode in Mode.explicit():
            components.append(GDT_Text(f"{self._name}_{mode.name.lower()}"))
        return components

    def get_editor(self) -> type['Editor']:
        return GDT_Editor.EDITORS[self._gdo.gdo_val(f"{self._name}_editor")]

    def get_input(self) -> str:
        return self._gdo.gdo_val(f"{self._name}")

    def converted_html(self) -> str:
        return self.get_editor().to_html(self.get_input())

    def get_output_gdt(self, mode: Mode) -> GDT:
        return self._gdo.column(self.get_output_gdt_key(mode))

    def get_output_gdt_key(self, mode: Mode) -> str:
        return f"{self._name}_{mode.name.lower()}"

    # #######
    # # GDT #
    # #######
    # def val(self, val: str):
    #     return self

    ##########
    # Render #
    ##########

    def render(self, mode: Mode = Mode.render_html):
        if mode in Mode.explicit():
            return self.get_rendered(mode)
        return super().render(mode)

    def render_form(self):
        return GDT_Template.python('message', 'form_message.html', {"field": self})

    def get_rendered(self, mode: Mode) -> str:
        gdt = self.get_output_gdt(mode)
        output = gdt.get_val()
        return output if output else self.get_rendered_now(gdt, mode)

    def get_rendered_now(self, gdt: GDT, mode: Mode) -> str:
        html = self.converted_html()
        tree = Editor.parse_tree(html)
        rendered = tree.render(mode)
        self._gdo.save_val(self.get_output_gdt_key(mode), rendered)
        return rendered
