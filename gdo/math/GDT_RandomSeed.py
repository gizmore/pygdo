from gdo.base.Util import Random
from gdo.core.GDT_UInt import GDT_UInt


class GDT_RandomSeed(GDT_UInt):

    _init_random: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.bytes(8)
        self._init_random = False

    def init_random(self, init_random: bool = True):
        self._init_random = init_random
        return self

    def gdo_before_create(self, gdo):
        if not self.get_val() and self._init_random:
            gdo.set_value(self._name, Random.mrand(1))
        return self
    