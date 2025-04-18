from gdo.base.GDT import GDT
from gdo.base.IPC import IPC
from gdo.base.Method import Method


class ipc_dogpid(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> [GDT]:
        return [
        ]

    def gdo_execute(self) -> GDT:
        IPC.PID = 0
        return self.empty()
