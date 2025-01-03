from gdo.base.Render import Render, Mode
from gdo.ui.GDT_Panel import GDT_Panel


class GDT_Success(GDT_Panel):

    def __init__(self):
        super().__init__()

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
