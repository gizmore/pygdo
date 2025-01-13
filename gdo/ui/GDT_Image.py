from gdo.base.Trans import t
from gdo.file.GDT_File import GDT_File
from gdo.message.WithHTMLAttributes import WithHTMLAttributes
from gdo.ui.WithHREF import WithHREF
from gdo.ui.WithSize import WithSize


class GDT_Image(WithSize, WithHREF, WithHTMLAttributes, GDT_File):
    _alt_key: str|None
    _alt_args: list|None

    def __init__(self, name: str):
        super().__init__(name)
        self._alt_key = None
        self._alt_args = None
        self._width = '100%'
        self._height = 'auto'

    def alternate(self, alt_key: str, alt_args: list = None):
        self._alt_key = alt_key
        self._alt_args = alt_args
        return self

    def alternate_raw(self, alt_text: str):
        return self.alternate('%s', [alt_text])

    ##########
    # Render #
    ##########
    def render_txt(self) -> str:
        return self.render_alt_text()

    def html_alternate(self) -> str:
        return f' alt="{self.render_alt_text()}"'

    def render_alt_text(self) -> str:
        return t(self._alt_key, self._alt_args) if self._alt_key else t('no_alt_text_an_image')

    def render_html(self) -> str:
        return f'<img{self.html_attrs()} src="{self.render_href()}"{self.html_alternate()} width="{self._width}" height="{self._height}" />'

    def render_form(self) -> str:
        return self.render_html()


