from gdo.base.Render import Mode
from gdo.core.GDT_Container import GDT_Container
from gdo.core.WithHTMLAttributes import WithHTMLAttributes


class GDT_Span(WithHTMLAttributes, GDT_Container):

    def get_tag(self) -> str:
        return 'span'

    def render(self, mode: Mode = Mode.render_html):
        if mode == Mode.render_html:
            return self._render_html()
        return self.render_gdt(mode)

    def render_html(self):
        return self._render_html()

    def render_fields(self, mode: Mode = Mode.render_html) -> str:
        return ''.join(gdt.render(mode) for gdt in self._fields)

    def render_txt(self):
        return self.render_fields(Mode.render_txt)

    def render_markdown(self):
        return self.render_fields(Mode.render_markdown)

    def render_cli(self):
        return self.render_fields(Mode.render_cli)

    def render_irc(self):
        return self.render_fields(Mode.render_irc)

    def render_telegram(self):
        return self.render_fields(Mode.render_telegram)

    def _render_html(self):
        tag = self.get_tag()
        attrs = self.html_attrs()
        attrs = f" {attrs}" if attrs else ''
        return f"<{tag}{attrs}>{super().render()}</{tag}>"
