from gdo.base.GDT import GDT
from gdo.base.Method import Method


class MethodCronjob(Method):

    def gdo_run_at(self) -> str:
        return "* * * * *"

    def gdo_user_permission(self) -> str | None:
        return 'cronjob'

    def gdo_trigger(self) -> str:
        return ''

    def gdo_execute(self) -> GDT:
        pass

