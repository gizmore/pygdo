from enum import Enum


class Mode(Enum):
    """
    Rendering Modes for GDTs
    """
    NIL = 0
    HTML = 1
    CELL = 2
    FORM = 3
    LIST = 4
    CARD = 5
    RES_6 = 6
    RES_7 = 7
    RES_8 = 8
    RES_9 = 9
    CLI = 10
    IRC = 11
    TELEGRAM = 12
    XML = 13
    JSON = 14
    MAIL = 15
    TXT = 16
    MARKDOWN = 17
    GTK = 18
    RSS = 19
    DOC = 20
    TOML = 21

    @classmethod
    def explicit(cls) -> list['Mode']:
        return [
            cls.HTML,
            cls.CLI,
            cls.IRC,
            cls.TELEGRAM,
            cls.MARKDOWN,
            cls.TXT,
        ]


class Render:
    """
    Text Rendering utility.
    Knows underline, bold, italic, green and red.
    Knows all the rendering modes.
    """

    @classmethod
    def green(cls, s: str, mode: Mode) -> str:
        """
        Turn text green.
        """
        match mode:
            case Mode.TXT | Mode.MARKDOWN | Mode.TELEGRAM:
                return s
            case Mode.CLI:
                return cls._cli_color(s, '2')
            case Mode.IRC:
                return cls._irc_color(s, '03')
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"green\">{s}</span>"
            case Mode.NIL | _:
                return f'green({mode.name})'

    @classmethod
    def red(cls, s: str, mode: Mode) -> str:
        """
        Turn text red.
        """
        match mode:
            case Mode.TXT | Mode.MARKDOWN | Mode.TELEGRAM:
                return s
            case Mode.CLI:
                return cls._cli_color(s, '1')
            case Mode.IRC:
                return cls._irc_color(s, '04')
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"red\">{s}</span>"
            case Mode.NIL | _:
                return f'red({mode.name})'

    @classmethod
    def bold(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return f"**{s}**"
            case Mode.CLI:
                return cls._cli_mode('1', s)
            case Mode.IRC:
                return f"\x02{s}\x02"
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST | Mode.TELEGRAM:
                return f"<b>{s}</b>"
            case Mode.NIL | _:
                return f'bold({mode.name} {s})'

    @classmethod
    def dim(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT:
                return s
            case Mode.MARKDOWN | Mode.TELEGRAM:
                return s
            case Mode.CLI:
                return cls._cli_mode('2', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"dim\">{s}</span>"
            case Mode.NIL | _:
                return f'dim({mode.name})'

    @classmethod
    def italic(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT:
                return f"/{s}/"
            case Mode.MARKDOWN:
                return f"*{s}*"
            case Mode.CLI:
                return cls._cli_mode('3', s)
            case Mode.IRC:
                return f"\x1D{s}\x1d"
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST | Mode.TELEGRAM:
                return f"<i>{s}</i>"
            case Mode.NIL | _:
                return f'italic({mode.name})'

    @classmethod
    def underline(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return f"_{s}_"
            case Mode.CLI:
                return cls._cli_mode('4', s)
            case Mode.IRC:
                return f"\x1f{s}\x1f"
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST | Mode.TELEGRAM:
                return f"<u>{s}</u>"
            case Mode.NIL | _:
                return f'underline({mode.name})'

    @classmethod
    def strike(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT | Mode.MARKDOWN | Mode.TELEGRAM:
                return f"~~{s}~~"
            case Mode.CLI:
                return cls._cli_mode('9', s)
            case Mode.IRC:
                return f"\x1e{s}\x1e"
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<strike>{s}</strike>"
            case Mode.NIL | _:
                return f'strike({mode.name})'

    @classmethod
    def blink(cls, s: str, mode: Mode):
        match mode:
            case Mode.TXT | Mode.MARKDOWN | Mode.TELEGRAM:
                return f"!{s}!"
            case Mode.CLI:
                return cls._cli_mode('5', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f'<span class="blink">{s}</span>'
            case Mode.NIL | _:
                return f'blink({mode.name})'

    @classmethod
    def invisible(cls, s: str, mode: Mode):
        match mode:
            case Mode.TXT | Mode.MARKDOWN | Mode.TELEGRAM:
                return '_' * len(s)
            case Mode.CLI:
                return cls._cli_mode('6', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f'<span class="invisible">{s}</span>'
            case Mode.NIL | _:
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
