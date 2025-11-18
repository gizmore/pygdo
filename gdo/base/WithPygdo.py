from gdo.base import Util


class WithPygdo:
    """
    Lazy global imports
    """

    Application = None
    Util = None
    Strings = None
    msg = None
    err = None
    html = None

    @classmethod
    def application(cls):
        if not cls.Application:
            from gdo.base.Application import Application
            cls.Application = Application
        return cls.Application

    @classmethod
    def util(cls, util: str=None):
        if not cls.Util:
            from gdo.base.Util import Strings, msg, html, err
            cls.Util = Util
            cls.Strings = Strings
            cls.msg = msg
            cls.err = err
            cls.html = html
        return getattr(cls, )
