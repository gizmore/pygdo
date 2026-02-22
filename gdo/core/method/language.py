from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import Trans
from gdo.core.GDT_Dict import GDT_Dict

class language(Method):

    def gdo_execute(self) -> GDT:
        return GDT_Dict(Trans.CACHE.get(Application.STORAGE.lang, Trans.EN))
