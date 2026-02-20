from gdo.base.Application import Application
from gdo.base.Cache import gdo_lru_cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import Trans
from gdo.core.GDT_Serialize import GDT_Serialize


class language(Method):

    @gdo_lru_cache(maxsize=None)
    def gdo_execute(self) -> GDT:
        return GDT_Serialize('lang').value(Trans.CACHE.get(Application.STORAGE.lang, Trans.EN))
