from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import module_enabled
from gdo.core.GDT_Container import GDT_Container
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class online(Method):

    def gdo_execute(self) -> GDT:
        grid = GDT_Container().add_class('user-online-grid')
        with_avatar = module_enabled('avatar')
        for user in self.gdo_module().online_users():
            grid.add_field(GDT_ProfileLink().user(user).with_avatar(with_avatar))
        return grid
