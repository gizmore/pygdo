from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_UInt import GDT_UInt


class db_raw(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "db.raw"

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.ADMIN

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_RestOfText('sql').not_null(),
            GDT_UInt('max_rows').max(100).initial('10'),
        ]

    def get_query(self) -> str:
        return self.param_value('sql').strip()

    def get_max_rows(self) -> int:
        return self.param_value('max_rows')

    def gdo_execute(self) -> GDT:
        out = []
        db = Application.db()
        query = self.get_query()
        ql = query.lower()
        max = self.get_max_rows()
        count = 0
        if ql.startswith('select ') or ql.startswith('show ') or ql.startswith('describe '):
            result = db.select(query)
            first = True
            while row := result.fetch_assoc():
                if first:
                    first = False
                    out.append('\t'.join(row.keys()))
                if count <= max:
                    out.append('\t'.join(list(map(str, row.values()))))
                count += 1
            if count > max:
                out.append(t('and_n_more', (count - max,)))
            return self.reply('%s', ("\n".join(out),))
        else:
            result = db.query(query)
            return self.reply('msg_db_raw_write', (result['info_msg'],))
