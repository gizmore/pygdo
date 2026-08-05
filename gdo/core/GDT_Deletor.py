from gdo.base.WithPygdo import WithPygdo
from gdo.core.GDT_User import GDT_User


class GDT_Deletor(GDT_User):

    def __init__(self, name: str):
        super().__init__(name)
        self.label('deletor')
        self.icon('user')

    def gdo_before_delete(self, gdo):
        GDO_User = WithPygdo.gdo_user()
        user = GDO_User.current()
        user = GDO_User.system() if user.is_ghost() else user
        gdo.set_val(self.get_name(), user.get_id())
        return self
