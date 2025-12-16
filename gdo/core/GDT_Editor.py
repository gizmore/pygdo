from typing import Self

from gdo.base.GDO import GDO
from gdo.core.GDT_User import GDT_User


class GDT_Editor(GDT_User):
    def __init__(self, name):
        super().__init__(name)
        self.not_null()

    def gdo(self, gdo: 'GDO') -> Self:
        self.gdo_before_update(gdo)
        return super().gdo(gdo)

    def gdo_before_update(self, gdo):
        from gdo.core.GDO_User import GDO_User
        user = GDO_User.current()
        user = GDO_User.system() if user.is_ghost() else user
        gdo.set_val(self.get_name(), user.get_id())
