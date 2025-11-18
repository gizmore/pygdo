from enum import Enum

from gdo.base.WithPygdo import WithPygdo

class Mode(Enum):
    """
    Rendering Modes for GDTs
    """
    nil = 0
    html = 1
    cell = 2
    form = 3
    list = 4
    card = 5
    RES_6 = 6
    RES_7 = 7
    RES_8 = 8
    RES_9 = 9
    cli = 10
    irc = 11
    telegram = 12
    xml = 13
    json = 14
    mail = 15
    txt = 16
    markdown = 17
    gtk = 18
    rss = 19
    doc = 20
    toml = 21

    @classmethod
    def explicit(cls) -> list['Mode']:
        return [
            cls.html,
            cls.cli,
            cls.irc,
            cls.telegram,
            cls.markdown,
            cls.txt,
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
            case Mode.txt | Mode.markdown | Mode.telegram:
                return s
            case Mode.cli:
                return cls._cli_color(s, '2')
            case Mode.irc:
                return cls._irc_color(s, '03')
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f"<span class=\"green\">{s}</span>"
            case Mode.nil | _:
                return f'green({mode.name})'

    @classmethod
    def red(cls, s: str, mode: Mode = None) -> str:
        """
        Turn text red.
        """
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown | Mode.telegram:
                return s
            case Mode.cli:
                return cls._cli_color(s, '1')
            case Mode.irc:
                return cls._irc_color(s, '04')
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f"<span class=\"red\">{s}</span>"
            case Mode.nil | _:
                return f'red({mode.name})'

    @classmethod
    def bold(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown:
                return f"**{s}**"
            case Mode.cli:
                return cls._cli_mode('1', s)
            case Mode.irc:
                return f"\x02{s}\x02"
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list | Mode.telegram:
                return f"<b>{s}</b>"
            case Mode.nil | _:
                return f'bold({mode.name} {s})'

    @classmethod
    def dim(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt:
                return s
            case Mode.markdown | Mode.telegram:
                return s
            case Mode.cli:
                return cls._cli_mode('2', s)
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f"<span class=\"dim\">{s}</span>"
            case Mode.nil | _:
                return f'dim({mode.name})'

    @classmethod
    def italic(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt:
                return f"/{s}/"
            case Mode.markdown:
                return f"*{s}*"
            case Mode.cli:
                return cls._cli_mode('3', s)
            case Mode.irc:
                return f"\x1D{s}\x1d"
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list | Mode.telegram:
                return f"<i>{s}</i>"
            case Mode.nil | _:
                return f'italic({mode.name})'

    @classmethod
    def underline(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown:
                return f"_{s}_"
            case Mode.cli:
                return cls._cli_mode('4', s)
            case Mode.irc:
                return f"\x1f{s}\x1f"
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list | Mode.telegram:
                return f"<u>{s}</u>"
            case Mode.nil | _:
                return f'underline({mode.name})'

    @classmethod
    def strike(cls, s: str, mode: Mode = None) -> str | list:
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown | Mode.telegram:
                return f"~~{s}~~"
            case Mode.cli:
                return cls._cli_mode('9', s)
            case Mode.irc:
                return f"\x1e{s}\x1e"
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f"<strike>{s}</strike>"
            case Mode.nil | _:
                return f'strike({mode.name})'

    @classmethod
    def blink(cls, s: str, mode: Mode = None):
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown | Mode.telegram:
                return f"!{s}!"
            case Mode.cli:
                return cls._cli_mode('5', s)
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f'<span class="blink">{s}</span>'
            case Mode.nil | _:
                return f'blink({mode.name})'

    @classmethod
    def invisible(cls, s: str, mode: Mode = None):
        mode = mode or cls.application().get_mode()
        match mode:
            case Mode.txt | Mode.markdown | Mode.telegram:
                return '_' * len(s)
            case Mode.cli:
                return cls._cli_mode('6', s)
            case Mode.html | Mode.cell | Mode.card | Mode.form | Mode.list:
                return f'<span class="invisible">{s}</span>'
            case Mode.nil | _:
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
