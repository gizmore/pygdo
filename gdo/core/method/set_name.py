from gdo.base.GDT import GDT
from gdo.base.Util import html
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserName import GDT_UserName


class set_name(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'name'

    @classmethod
    def gdo_trig(cls) -> str:
        return 'setname'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('user').not_null().positional().with_completion(),
            GDT_UserName('displayname').not_null().positional(),
        ]

    def gdo_execute(self) -> GDT:
        user = self.param_value('user')
        displayname = self.param_val('displayname')
        count = GDO_User.table().count_where(
            f"user_server={user.get_server_id()} AND user_displayname={GDT.quote(displayname)} AND user_id != {user.get_id()} AND user_link IS NULL"
        )
        if count:
            return self.err('err_username_taken')
        user.save_val('user_displayname', displayname)
        return self.reply('msg_username_set_for', (user.get_name_sid(), html(displayname)))
