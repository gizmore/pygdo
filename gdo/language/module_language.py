from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.language.GDO_Language import GDO_Language
from gdo.language.GDT_Language import GDT_Language
from gdo.language.InstallLanguage import InstallLanguage


class module_language(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 2

    def gdo_classes(self):
        return [
            GDO_Language,
        ]

    async def gdo_install(self):
        InstallLanguage.now()

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Language('language').not_null().icon('language').initial('en').tooltip('tt_core_language'),
        ]

    def get_language(self, user: GDO_User) -> GDO_Language:
        return user.get_setting_value('language')

    def get_language_iso(self, user: GDO_User) -> str:
        return user.get_setting_val('language')
