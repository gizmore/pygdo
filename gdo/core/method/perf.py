from gdo.base.Method import Method
from gdo.core.GDT_Perf import GDT_Perf


class perf(Method):

    def gdo_execute(self):
        return GDT_Perf()
