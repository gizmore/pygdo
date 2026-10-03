from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.Render import Mode
from gdo.base.Trans import t
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.table.MethodQueryCards import MethodQueryCards
from gdo.ui.GDT_Card import GDT_Card
from gdo.ui.GDT_Link import GDT_Link


class linked(MethodQueryCards):
    """Show every connector account belonging to one linked-account group."""

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_User('user').not_null()]

    def get_master(self) -> GDO_User:
        return self.param_value('user').get_effective_user()

    def gdo_render_title(self) -> str:
        return t('mt_account_linked', (self.get_master().render_name(),))

    def gdo_render_descr(self) -> str:
        return t('md_account_linked', (self.get_master().render_name(),))

    def gdo_table(self) -> GDO:
        return GDO_User.table()

    def gdo_table_query(self) -> Query:
        master = self.get_master()
        return super().gdo_table_query().where(
            f'user_id={master.get_id()} OR user_link={master.get_id()}'
        )

    def gdo_paginated(self) -> bool:
        return False

    def gdo_ordered(self) -> bool:
        return False

    def gdo_filtered(self) -> bool:
        return False

    def gdo_searched(self) -> bool:
        return False

    def render_gdo(self, gdo: GDO, mode: Mode):
        user = gdo
        if mode == Mode.render_json:
            return {
                'id': user.get_id(),
                'name': user.get_name(),
                'server': user.get_server().get_name(),
            }
        card = GDT_Card().title_raw(user.render_name())
        card.get_content().add_fields(
            GDT_Link().href(
                href('user', 'profile', f'&for={user.get_id()}-{user.get_name()}')
            ).text('profile').icon('face'),
            user.column('user_server'),
        )
        return card.render(mode)
