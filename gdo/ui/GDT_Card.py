from gdo.avatar.GDT_Avatar import GDT_Avatar
from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Util import module_enabled
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Template import GDT_Template
from gdo.core.WithGDO import WithGDO
from gdo.date.GDT_Created import GDT_Created
from gdo.ui.GDT_Image import GDT_Image
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle


class GDT_Card(WithGDO, WithText, WithTitle, GDT):
    _image: GDT_Image
    _header: GDT_Container
    _content: GDT_Container
    _footer: GDT_Container

    def __init__(self):
        super().__init__()
        self._header = GDT_Container()
        self._content = GDT_Container()
        self._footer = GDT_Container()

    def image(self, image: GDT_Image):
        self._image = image
        return self

    def has_image(self) -> bool:
        return hasattr(self, '_image')

    def get_header(self) -> GDT_Container:
        # if not hasattr(self, '_header'):
        #     self._header = GDT_Container()
        return self._header

    def get_content(self) -> GDT_Container:
        # if not hasattr(self, '_content'):
        #     self._content = GDT_Container()
        return self._content

    def get_footer(self) -> GDT_Container:
        # if not hasattr(self, '_footer'):
        #     self._footer = GDT_Container()
        return self._footer

    def creator_header(self):
        creator = self._gdo.column_of(GDT_Creator)
        created = self._gdo.column_of(GDT_Created)
        self.get_header().add_fields(creator, created)
        if module_enabled('avatar'):
            self.get_header().add_field(GDT_Avatar('avatar').for_user(creator.get_value()))
        return self

    def render(self, mode: Mode = Mode.render_html):
        if mode.is_html():
            return self.render_html()
        if mode.is_textual():
            return self.render_text(mode)
        return super().render(mode)

    def render_html(self) -> str:
        return GDT_Template.python('ui', 'card.html', {
            'field': self,
        })

    def render_text(self, mode: Mode = Mode.render_html):
        text = self._header.render(mode)
        text += ' - '
        text += self._content.render(mode)
        text += ' - '
        text += self._footer.render(mode)
        return text.strip(' -')
