from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.table.MethodQueryTable import MethodQueryTable


class users(MethodQueryTable):

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_table(self) -> GDO:
        return GDO_User.table()

    def setting_fields(self) -> list[GDT]:
        ModuleLoader.instance().init_user_settings()
        fields = []
        for name, template in sorted(GDT_UserSetting.KNOWN.items()):
            if not isinstance(template, GDT_Field) or template.is_secret():
                continue
            field = template.copy_as(name)
            render_cell = field.render_cell

            def render_setting_cell(field=field, render_cell=render_cell) -> str:
                return render_cell() if field.get_val() is not None else '---'

            field.render_cell = render_setting_cell
            fields.append(field)
        return fields

    def gdo_table_headers(self) -> list[GDT]:
        return super().gdo_table_headers() + self.setting_fields()

    def gdo_table_query(self) -> Query:
        query = super().gdo_table_query()
        for gdt in self.setting_fields():
            GDO_User.join_setting(query, gdt.get_name())
        return query

    def gdo_table_search_query(self, query: Query, term: str):
        if term:
            escaped = GDT.escape_search(term)
            query.search_where(
                "EXISTS (SELECT 1 FROM gdo_usersetting "
                "WHERE uset_user=gdo_user.user_id "
                f"AND uset_val LIKE '%{escaped}%')")
