from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Query import Query
from gdo.base.Util import Strings
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_ObjectSelect import GDT_ObjectSelect


class GDT_Channel(GDT_ObjectSelect):

    _default_current: bool

    def __init__(self, name):
        super().__init__(name)
        self.table(GDO_Channel.table())
        self._default_current = False

    def default_current(self, default_current: bool = True):
        self._default_current = default_current
        return self

    def to_value(self, val: str):
        if not val and self._default_current:
            return Message.CURRENT._env_channel
        return super().to_value(val)

    def query_gdos_query(self, val: str, query: Query) -> Query:
        val_serv = Strings.regex_first(r'{([^{}]+)}$', val)
        val = Strings.substr_to(val, '{', val)
        query.where(f"chan_displayname LIKE '%{GDT.escape(val)}%'")
        if val_serv:
            from gdo.core.GDO_Server import GDO_Server
            if server := GDO_Server.table().get_by_vals({'serv_name': val_serv}):
                query.where(f"chan_server={server.get_id()}")
            elif val_serv.isdecimal():
                query.where(f"chan_server={val_serv}")
            else:
                query.where('1=0')
        return query

    def query_gdos(self, val: str) -> list[GDO]:
        if val.isdecimal():
            if channel := self._table.get_by_aid(val):
                return [channel]
            return []
        return self.query_gdos_query(val, self._table.select()).limit(10).exec().fetch_all()
