class WithGDO():
    _gdo: object

    def gdo(self, gdo: object):
        self._gdo = gdo
        return self
