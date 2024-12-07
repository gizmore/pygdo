from gdo.core.GDT_User import GDT_User


class GDT_Creator(GDT_User):
    def __init__(self, name):
        super().__init__(name)
        self.not_null()

    def gdo_before_create(self, gdo):
        from gdo.core.GDO_User import GDO_User
        user = GDO_User.current()
        if user.is_ghost():
            user = GDO_User.system()
        gdo.set_val(self.get_name(), user.get_id())
