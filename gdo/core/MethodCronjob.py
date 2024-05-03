from gdo.base.Method import Method


class MethodCronjob(Method):

    def gdo_trigger(self) -> str:
        return ''

    def execute(self):
        pass
