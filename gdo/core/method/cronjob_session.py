from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.core.GDO_Session import GDO_Session
from gdo.core.MethodCronjob import MethodCronjob
from gdo.date.Time import Time


class cronjob_session(MethodCronjob):

    def gdo_execute(self) -> GDT:
        cut = Time.get_date(Application.TIME - GDO_Session.LIFETIME)
        GDO_Session.table().delete_where(f'sess_time < "{cut}"')
        return self.empty()
