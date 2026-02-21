class WithPygdo:
    """
    Lazy global imports
    """
    Application = None
    Files = None
    Util = None
    Strings = None
    msg = None
    err = None
    html = None
    GDT_String = None
    GDO_User = None
    GDT_Page = None
    GDT_Error = None
    GDT_Success = None
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
    def gdt_error():
        if not WithPygdo.GDT_Error:
            from gdo.ui.GDT_Error import GDT_Error
            WithPygdo.GDT_Error = GDT_Error
        return WithPygdo.GDT_Error

    @staticmethod
    def gdt_success():
        if not WithPygdo.GDT_Success:
            from gdo.ui.GDT_Success import GDT_Success
            WithPygdo.GDT_Success = GDT_Success
        return WithPygdo.GDT_Success

    @staticmethod
    def util(util: str=None):
        if not WithPygdo.Util:
            from gdo.base.Util import Strings, msg, html, err, Files
            WithPygdo.Util = True
            WithPygdo.Files = Files
            WithPygdo.Strings = Strings
            WithPygdo.msg = msg
            WithPygdo.err = err
            WithPygdo.html = html
        return getattr(WithPygdo, util)
