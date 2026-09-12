from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Util import html
from gdo.base.WithName import WithName
from gdo.core.GDT_Field import GDT_Field
from gdo.ui.WithText import WithText


class GDT_Button(WithName, WithText, GDT_Field):
    _call: callable

    def __init__(self, name: str):
        super().__init__(name)
        self._default_button = False

    def default_button(self, default_button: bool = True):
        self._default_button = default_button
        return self

    def calling(self, call: callable):
        self._call = call
        return self

    def href(self, href: str):
        self._href = href
        return self

    def render_href(self) -> str:
        href = getattr(self, '_href', '')
        if gdo := self.get_gdo():
            identifier = str(gdo.get_id())
            href = href.replace('%ID%', identifier).replace('%25ID%25', identifier)
        return html(href)

    def render_html(self) -> str:
        text = self.render_text() if self.has_text() else html(self.get_val() or self.get_name())
        content = f'{self.render_icon(Mode.render_html)}<span>{text}</span>'
        if hasattr(self, '_href'):
            return f'<a class="gdt-button" href="{self.render_href()}"{self.html_attrs()}>{content}</a>'
        return f'<button class="gdt-button" type="button"{self.html_attrs()}>{content}</button>'

    def call(self) -> GDT:
        return self._call()
