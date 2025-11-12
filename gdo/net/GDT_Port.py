from gdo.core.GDT_UInt import GDT_UInt


class GDT_Port(GDT_UInt):

    def __init__(self, name: str):
        super().__init__(name)
        self.min(1)
        self.max(65535)
        self.bytes(2)
        self.unsigned()
