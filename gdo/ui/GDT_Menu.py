from gdo.core.GDT_Container import GDT_Container


class GDT_Menu(GDT_Container):

    def __init__(self):
        super().__init__()

    def render_form(self):
        return f'<div class="gdt-menu">{super().render_form()}</div>'
