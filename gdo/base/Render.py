from enum import Enum
from functools import lru_cache

from gdo.base.WithPygdo import WithPygdo

class Mode(Enum):
    """
    Rendering Modes for GDTs
    """
    render_nil = 0
    render_html = 1
    render_cell = 2
    render_form = 3
    render_list = 4
    render_card = 5
    RES_6 = 6
    RES_7 = 7
    RES_8 = 8
    RES_9 = 9
    render_cli = 10
    render_irc = 11
    render_telegram = 12
    render_xml = 13
    render_json = 14
    render_mail = 15
    render_txt = 16
    render_markdown = 17
    render_gtk = 18
    render_rss = 19
    render_doc = 20
    render_toml = 21

    @staticmethod
    @lru_cache
    def explicit() -> 'list[Mode]':
        return [
            Mode.render_html,
            Mode.render_cli,
            Mode.render_irc,
            Mode.render_telegram,
            Mode.render_markdown,
            Mode.render_txt,
        ]

    def is_html(self) -> bool:
        return self.value < 10

    def is_textual(self):
        return not self.is_html()


class Render(WithPygdo):
    """
    Text Rendering utility.
    Knows underline, bold, italic, green and red.
    Knows all the rendering modes.
    """

    @classmethod
    def green(cls, s: str, mode: Mode = None) -> str:
        """
        Turn text green.
        """
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown | Mode.render_telegram:
                return s
            case Mode.render_cli:
                return cls._cli_color(s, '2')
            case Mode.render_irc:
                return cls._irc_color(s, '03')
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f"<span class=\"green\">{s}</span>"
            case Mode.render_nil | _:
                return f'green({mode.name})'

    @classmethod
    def red(cls, s: str, mode: Mode = None) -> str:
        """
        Turn text red.
        """
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown | Mode.render_telegram:
                return s
            case Mode.render_cli:
                return cls._cli_color(s, '1')
            case Mode.render_irc:
                return cls._irc_color(s, '04')
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f"<span class=\"red\">{s}</span>"
            case Mode.render_nil | _:
                return f'red({mode.name})'

    @classmethod
    def bold(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown:
                return f"**{s}**"
            case Mode.render_cli:
                return cls._cli_mode('1', s)
            case Mode.render_irc:
                return f"\x02{s}\x02"
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list | Mode.render_telegram:
                return f"<b>{s}</b>"
            case Mode.render_nil | _:
                return f'bold({mode.name} {s})'

    @classmethod
    def dim(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt:
                return s
            case Mode.render_markdown | Mode.render_telegram:
                return s
            case Mode.render_cli:
                return cls._cli_mode('2', s)
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f"<span class=\"dim\">{s}</span>"
            case Mode.render_nil | _:
                return f'dim({mode.name})'

    @classmethod
    def italic(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt:
                return f"/{s}/"
            case Mode.render_markdown:
                return f"*{s}*"
            case Mode.render_cli:
                return cls._cli_mode('3', s)
            case Mode.render_irc:
                return f"\x1D{s}\x1d"
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list | Mode.render_telegram:
                return f"<i>{s}</i>"
            case Mode.render_nil | _:
                return f'italic({mode.name})'

    @classmethod
    def underline(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown:
                return f"_{s}_"
            case Mode.render_cli:
                return cls._cli_mode('4', s)
            case Mode.render_irc:
                return f"\x1f{s}\x1f"
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list | Mode.render_telegram:
                return f"<u>{s}</u>"
            case Mode.render_nil | _:
                return f'underline({mode.name})'

    @classmethod
    def strike(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown | Mode.render_telegram:
                return f"~~{s}~~"
            case Mode.render_cli:
                return cls._cli_mode('9', s)
            case Mode.render_irc:
                return f"\x1e{s}\x1e"
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f"<strike>{s}</strike>"
            case Mode.render_nil | _:
                return f'strike({mode.name})'

    @classmethod
    def blink(cls, s: str, mode: Mode = None):
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown | Mode.render_telegram:
                return f"!{s}!"
            case Mode.render_cli:
                return cls._cli_mode('5', s)
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f'<span class="blink">{s}</span>'
            case Mode.render_nil | _:
                return f'blink({mode.name})'

    @classmethod
    def invisible(cls, s: str, mode: Mode = None):
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.render_txt | Mode.render_markdown | Mode.render_telegram:
                return '_' * len(s)
            case Mode.render_cli:
                return cls._cli_mode('6', s)
            case Mode.render_html | Mode.render_cell | Mode.render_card | Mode.render_form | Mode.render_list:
                return f'<span class="invisible">{s}</span>'
            case Mode.render_nil | _:
                return f'invisible({mode.name})'

    ###########
    # Private #
    ###########

    @classmethod
    def _cli_mode(cls, typ: str, s: str):
        return f"\033[%sm%s\033[0m" % (typ, s)

    @classmethod
    def _cli_color(cls, s: str, color: str):
        return f"\033[3{color}m{s}\033[0m"

    @classmethod
    def _irc_color(cls, s: str, color: str):
        return f"\x03{color},99{s}\x03"
