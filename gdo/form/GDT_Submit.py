from gdo.base.Render import Mode
from gdo.ui.GDT_Button import GDT_Button


class GDT_Submit(GDT_Button):

    def __init__(self, name: str = 'submit'):
        super().__init__(name)
        self.name(name)
        self.text('submit')

    def render_form(self):
        return f'<span class="gdt-submit"><input type="submit" name="{self.get_name()}" value="{self.render_text(Mode.HTML)}"></span>'



