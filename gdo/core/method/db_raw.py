from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_RestOfText import GDT_RestOfText


class db_raw(Method):

    def gdo_trigger(self) -> str:
        return "db.raw"

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.ADMIN

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_RestOfText('sql').not_null(),
        ]

    def get_query(self) -> str:
        return self.param_value('sql').strip()

    def gdo_execute(self):
        out = []
        db = Application.db()
        query = self.get_query()
        ql = query.lower()
        if ql.startswith('select ') or ql.startswith('show '):
            result = db.select(query)
            first = True
            while row := result.fetch_assoc():
                if first:
                    first = False
                    out.append('\t'.join(row.keys()))
                out.append('\t'.join(list(map(str, row.values()))))
            return self.reply('%s', ["\n".join(out)])
        else:
            result = db.query(query)
            return self.reply('msg_db_raw_write', [result['info_msg']])
