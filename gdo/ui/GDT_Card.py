from gdo.base.GDT import GDT
from gdo.base.Render import Mode, Render
from gdo.base.Util import module_enabled
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Creator import GDT_Creator
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Template import GDT_Template
from gdo.core.WithHTMLAttributes import WithHTMLAttributes
from gdo.core.WithGDO import WithGDO
from gdo.base.WithName import WithName
from gdo.date.GDT_Created import GDT_Created
from gdo.ui.WithText import WithText
from gdo.ui.WithTitle import WithTitle
from gdo.ui.WithImage import WithImage


class GDT_Card(WithHTMLAttributes, WithImage, WithGDO, WithText, WithTitle, GDT):
    _image: GDT
    _header: GDT_Container
    _content: GDT_Container
    _footer: GDT_Container

    def __init__(self):
        super().__init__()
        self._header = GDT_Container()
        self._content = GDT_Container()
        self._footer = GDT_Container()

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
            from gdo.avatar.GDT_Avatar import GDT_Avatar
            self.get_header().add_field(GDT_Avatar('avatar').for_user(creator.get_value()))
        return self

    def render(self, mode: Mode = Mode.render_html):
        if mode.is_textual():
            return self.render_text(mode)
        return super().render(mode)

    def render_html(self) -> str:
        return GDT_Template.python('ui', 'card.html', {
            'field': self,
        })

    def render_text(self, mode: Mode = Mode.render_html) -> str:
        return ' | '.join(filter(None, (
            self.render_title(),
            self.render_text_section(self._header, mode),
            self.render_text_section(self._content, mode),
            self.render_text_section(self._footer, mode),
        )))

    def render_txt(self) -> str:
        """Pages call explicit TXT renderers directly, bypassing ``render``."""
        return self.render_text(Mode.render_txt)

    def render_json(self) -> dict:
        """Render cards as stable data rather than an implementation name."""
        return {
            'title': self.render_title() if self.has_title() else None,
            'header': self.render_json_section(self._header),
            'content': self.render_json_section(self._content),
            'footer': self.render_json_section(self._footer),
        }

    @staticmethod
    def render_text_section(section: GDT_Container, mode: Mode) -> str:
        """Render Card fields as labelled values for CLI/chat output."""
        out = []
        for field in section.get_fields():
            value = field.render(mode)
            if not value:
                continue
            if isinstance(field, GDT_Field):
                value = f'{field.render_label(mode)}: {Render.bold(value, mode)}'
            out.append(value)
        return ' | '.join(out)

    @staticmethod
    def render_json_section(section: GDT_Container) -> list[dict]:
        """Keep both named fields and anonymous display snippets representable."""
        out = []
        for field in section.get_fields():
            out.append({
                'name': field.get_name() if isinstance(field, (GDT_Field, WithName)) else None,
                'value': field.render(Mode.render_json),
            })
        return out
