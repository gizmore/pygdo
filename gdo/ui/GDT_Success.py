from gdo.base.Logger import Logger
from gdo.base.Render import Render, Mode
from gdo.base.Trans import Trans
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Success(GDT_Panel):

    _no_log: bool

    def __init__(self):
        super().__init__()
        self._no_log = False

    def no_log(self, no_log: bool = True):
        self._no_log = no_log
        return self

    def html_class(self):
        return 'gdt-success alert alert-success'

    def render(self, mode: Mode = Mode.HTML):
        if not self._no_log:
            with Trans('en'):
                Logger.message(self.render_txt())
        return super().render(mode)

    def render_txt(self):
        return self.render_text(Mode.TXT)

    def render_cli(self):
        return Render.green(self.render_text(Mode.CLI), Mode.CLI)

    def render_telegram(self):
        return Render.green(self.render_text(Mode.TELEGRAM), Mode.TELEGRAM)

    def render_irc(self) -> str:
        return Render.green(self.render_text(Mode.IRC), Mode.IRC)

    # def render_html(self):
    #     return Render.green(f"{self.render_title(Mode.HTML)}: {self.render_text(Mode.HTML)}", Mode.HTML)
