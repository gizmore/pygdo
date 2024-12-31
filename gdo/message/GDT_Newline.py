from gdo.base.GDT import GDT


class GDT_Newline(GDT):

    def render_cli(self):
        return "\n"

    def render_html(self):
        return "<br/>"
