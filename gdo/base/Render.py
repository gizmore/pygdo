from enum import Enum

from gdo.base.GDT import GDT


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
            case Mode.TXT | Mode.MARKDOWN:
                return s
            case Mode.CLI:
                return cls._cli_color(s, '1')
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"green\">{s}</span>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def red(cls, s: str, mode: Mode) -> str:
        """
        Turn text red.
        """
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return s
            case Mode.CLI:
                return cls._cli_color(s, '2')
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"red\">{s}</span>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def bold(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return f"*{s}*"
            case Mode.CLI:
                return cls._cli_mode('1', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<b>{s}</b>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def dim(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT:
                return s
            case Mode.MARKDOWN:
                return s
            case Mode.CLI:
                return cls._cli_mode('2', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<span class=\"dim\">{s}</span>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def italic(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT:
                return "/{s}/"
            case Mode.MARKDOWN:
                return f"**{s}**"
            case Mode.CLI:
                return cls._cli_mode('3', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<i>{s}</i>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def underline(cls, s: str, mode: Mode) -> str | list:
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return f"_{s}_"
            case Mode.CLI:
                return cls._cli_mode('4', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f"<u>{s}</u>"
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def blink(cls, s: str, mode: Mode):
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return f"!{s}!"
            case Mode.CLI:
                return cls._cli_mode('5', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f'<span class="blink">{s}</span>'
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    @classmethod
    def invisible(cls, s: str, mode: Mode):
        match mode:
            case Mode.TXT | Mode.MARKDOWN:
                return '_' * len(s)
            case Mode.CLI:
                return cls._cli_mode('6', s)
            case Mode.HTML | Mode.CELL | Mode.CARD | Mode.FORM | Mode.LIST:
                return f'<span class="invisible">{s}</span>'
            case Mode.NIL | _:
                return GDT.EMPTY_STRING

    ###########
    # Private #
    ###########

    @classmethod
    def _cli_mode(cls, typ: str, s: str):
        return f"\\033[%sm%s\\033[0m" % (typ, s)

    @classmethod
    def _cli_color(cls, s: str, color: str):
        return f"\\033[3{color}m{s}\\033[0m"
