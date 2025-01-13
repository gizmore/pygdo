from gdo.base.GDT import GDT
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Template import GDT_Template
from gdo.core.WithGDO import WithGDO
from gdo.ui.GDT_Image import GDT_Image
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Card(WithGDO, WithText, WithTitle, GDT):
    _image: GDT_Image
    _header: GDT_Container
    _content: GDT_Container
    _footer: GDT_Container

    def image(self, image: GDT_Image):
        self._image = image
        return self

    def has_image(self) -> bool:
        return hasattr(self, '_image')

    def get_header(self) -> GDT_Container:
        if not hasattr(self, '_header'):
            self._header = GDT_Container()
        return self._header

    def get_content(self) -> GDT_Container:
        if not hasattr(self, '_content'):
            self._content = GDT_Container()
        return self._content

    def get_footer(self) -> GDT_Container:
        if not hasattr(self, '_footer'):
            self._footer = GDT_Container()
        return self._footer

    def render_html(self) -> str:
        return GDT_Template.python('ui', 'card.html', {
            'field': self,
        })
