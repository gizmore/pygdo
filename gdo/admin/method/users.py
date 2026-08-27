from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Query import Query
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.core.WithObject import WithObject
from gdo.table.MethodQueryTable import MethodQueryTable


class users(MethodQueryTable):

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_paginate_size(self) -> int:
        return 50

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
            filter_query = field.gdo_filter_query
            search_query = field.gdo_search_query
            column = f'setting_{name}.uset_val'

            def render_setting_cell(field=field, render_cell=render_cell) -> str:
                return render_cell() if field.get_val() is not None else '---'

            def use_setting_column(callback, *args, field=field, column=column):
                original_name = field.get_name()
                field.name(column)
                try:
                    return callback(*args)
                finally:
                    field.name(original_name)

            def filter_setting_query(gdo, query, callback=filter_query, use_column=use_setting_column):
                return use_column(callback, gdo, query)

            if isinstance(field, WithObject):
                def filter_setting_object_query(gdo, query, field=field, column=column):
                    if not (value := field.get_val()):
                        return
                    table = field._table
                    primary = table.primary_key_column()
                    if name := table.name_column():
                        subquery = table.select().only_select(primary.get_name())
                        name.copy_as(name.get_name()).val(value).gdo_filter_query(table, subquery)
                        query.where(f'{column} IN ({subquery.build_query()})')
                    else:
                        query.where(f'{column}={GDT.quote(value)}')

                filter_setting_query = filter_setting_object_query

            def search_setting_query(query, term, callback=search_query, use_column=use_setting_column):
                return use_column(callback, query, term)

            field.render_cell = render_setting_cell
            field.gdo_filter_query = filter_setting_query
            field.gdo_search_query = search_setting_query
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
