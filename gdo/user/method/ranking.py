from gdo.base.GDO import GDO
from gdo.base.Render import Mode
from gdo.base.Util import module_enabled
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Server import GDT_Server
from gdo.core.GDT_UserName import GDT_UserName
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.user.GDT_Level import GDT_Level
from gdo.user.GDT_ProfileLink import GDT_ProfileLink


class ranking(MethodQueryTable):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'users'

    def gdo_table(self) -> GDO:
        return GDO_User.table()

    def gdo_table_headers(self) -> list:
        headers = []
        if module_enabled('country'):
            from gdo.country.GDT_Country import GDT_Country
            headers.append(GDT_Country('country'))
        headers.extend([
            GDT_Level('level'),
            GDT_UserName('user_name').label('username'),
        ])
        headers.append(GDT_Server('user_server').label('server'))
        return headers

    def gdo_table_query(self):
        query = GDO_User.table().select()
        GDO_User.join_setting(query, 'level')
        if module_enabled('country'):
            GDO_User.join_setting(query, 'country_living', 'country')
        return query

    def gdo_order_default(self):
        return 'level DESC'

    def render_user_name(self, _field, user: GDO_User):
        return GDT_ProfileLink().with_avatar(module_enabled('avatar')).user(user).render(Mode.render_cell)
