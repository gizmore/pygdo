from gdo.base.GDT import GDT
from gdo.base.IPC import IPC
from gdo.base.Method import Method


class ipc_dogpid(Method):
    """
    Clear the IPC dog pid.
    Triggered when dog or repl boots.
    """

    def gdo_execute(self) -> GDT:
        IPC.PID = 0
        return self.empty()
