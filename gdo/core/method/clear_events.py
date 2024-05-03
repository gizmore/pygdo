from gdo.core.MethodCronjob import MethodCronjob


class clear_events(MethodCronjob):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_execute(self):
        pass
