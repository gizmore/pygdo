from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.Method import Method


class usage(Method):

    def gdo_trigger(self) -> str:
        return ''

    def gdo_execute(self):
        Logger.error('USAGE for ' + Application.environ('REMOTE_ADDR'))