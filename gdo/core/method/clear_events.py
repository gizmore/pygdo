from gdo.base.GDT import GDT
from gdo.core.MethodCronjob import MethodCronjob


class clear_events(MethodCronjob):

    def gdo_run_at(self) -> str:
        return self.run_daily_at(4)

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'core.ce'

    def gdo_execute(self) -> GDT:
        pass
