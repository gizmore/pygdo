import sys

import better_exceptions

from gdo.base.Logger import Logger
from gdo.base.Render import Render, Mode
from gdo.base.Trans import Trans
from gdo.base.Util import html
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Error(GDT_Panel):

    _trace: bool

    def __init__(self):
        super().__init__()
        self._trace = False

    def trace(self, trace: bool = True):
        self._trace = trace
        return self

    def html_class(self):
        if self._trace:
            return 'gdt-exception'
        return super().html_class()

    def render(self, mode: Mode = Mode.HTML):
        if not self._trace:
            with Trans('en'):
                Logger.error(self.render_text(Mode.TXT))
        return super().render(mode)

    def render_txt(self):
        return "!!! " + self.render_text(Mode.TXT)

    def render_cli(self):
        return Render.red(self.render_text(Mode.CLI), Mode.CLI)

    def render_irc(self) -> str:
        return Render.red(self.render_text(Mode.IRC), Mode.IRC)

    def render_telegram(self):
        return Render.red(self.render_text(Mode.TELEGRAM), Mode.TELEGRAM)

    @classmethod
    def from_exception(cls, ex: Exception, title: str = 'PyGDO'):
        Logger.exception(ex)
        text = html(str(ex))
        trace = html("".join(better_exceptions.format_exception(*sys.exc_info())))
        return cls().trace().title_raw(title).text_raw(f"<pre>{text}\n{trace}</pre>\n", False)
