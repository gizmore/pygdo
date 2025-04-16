from gdo.base.GDT import GDT
from gdo.base.Method import Method


class MethodCronjob(Method):

    def gdo_run_at(self) -> str:
        return "* * * * *"

    def run_daily_at(self, hour: str|int, minute: str = "0") -> str:
        return f"* * * {hour} {minute}"

    def gdo_user_permission(self) -> str | None:
        return 'cronjob'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_execute(self) -> GDT:
        pass
