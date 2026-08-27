from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.core.WithFields import WithFields
from gdo.ui.WithFlow import WithFlow


class GDT_Container(WithFlow, WithFields, GDT):

    __slots__ = (
        '_fields',
    )

    def __init__(self):
        super().__init__()
        self._fields = []
        self.horizontal()

    def render(self, mode: Mode = Mode.render_html):
        """Dispatch through GDT rather than WithFields.

        ``WithFields.render`` otherwise wins the MRO and renders only the
        children, silently dropping this container's own HTML wrapper.
        Nested containers then cannot provide their flow or CSS classes.
        """
        if mode in (Mode.render_cli, Mode.render_irc, Mode.render_telegram,
                    Mode.render_txt, Mode.render_markdown, Mode.render_mail,
                    Mode.render_rss, Mode.render_doc):
            return self.render_fields(mode)
        return GDT.render(self, mode)

    def render_html(self) -> str:
        return f'<div class="gdt-container {self.render_class()}">{self.render_fields()}</div>\n'

    def render_list(self) -> str:
        return self.render_fields(Mode.render_list)

    def render_card(self) -> str:
        return self.render_fields(Mode.render_card)
