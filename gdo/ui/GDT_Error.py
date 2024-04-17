import os
import sys
import traceback

from gdo.base.Logger import Logger
from gdo.base.Render import Render, Mode
from gdo.base.Trans import t
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Error(GDT_Panel):

    def __init__(self):
        super().__init__()

    def render_cli(self):
        return Render.red(f"{t('error')}: {self.render_title(Mode.CLI)}: {self.render_text(Mode.CLI)}", Mode.CLI)

    # def render_html(self):
    #     return Render.red(f"{t('error')}: {self.render_title(Mode.HTML)}: {self.render_text(Mode.HTML)}", Mode.HTML)

    @classmethod
    def from_exception(cls, ex: Exception, title: str = 'Core'):
        Logger.exception(ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        line = exc_tb.tb_lineno
        return cls().title_raw(title).text_raw(str(ex) + f"{exc_type} in {file} line {line}\nBacktrace:\n{traceback.format_exc()}\n")
