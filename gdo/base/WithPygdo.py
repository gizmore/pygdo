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
    GDT_String = None
    GDO_User = None
    GDT_Page = None
    ModuleLoader = None

    @staticmethod
    def loader():
        if not WithPygdo.ModuleLoader:
            from gdo.base.ModuleLoader import ModuleLoader
            WithPygdo.ModuleLoader = ModuleLoader.instance()
        return WithPygdo.ModuleLoader

    @staticmethod
    def gdt_string():
        if not WithPygdo.GDT_String:
            from gdo.core.GDT_String import GDT_String
            WithPygdo.GDT_String = GDT_String
        return WithPygdo.GDT_String

    @staticmethod
    def gdo_user():
        if not WithPygdo.GDO_User:
            from gdo.core.GDO_User import GDO_User
            WithPygdo.GDO_User = GDO_User
        return WithPygdo.GDO_User

    @staticmethod
    def application():
        if not WithPygdo.Application:
            from gdo.base.Application import Application
            WithPygdo.Application = Application
        return WithPygdo.Application

    @staticmethod
    def gdt_page():
        if not WithPygdo.GDT_Page:
            from gdo.ui.GDT_Page import GDT_Page
            WithPygdo.GDT_Page = GDT_Page
        return WithPygdo.GDT_Page

    @staticmethod
    def util(util: str=None):
        if not WithPygdo.Util:
            from gdo.base.Util import Strings, msg, html, err
            WithPygdo.Util = Util
            WithPygdo.Strings = Strings
            WithPygdo.msg = msg
            WithPygdo.err = err
            WithPygdo.ahtml = html
        return getattr(WithPygdo, util)
