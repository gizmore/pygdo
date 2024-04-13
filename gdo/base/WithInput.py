class WithInput:

    _input: dict

    def input(self, key, val):
        if not hasattr(self, '_input'):
            self._input = {}
        self._input[key] = val
        return self

    def inputs(self, vals: dict):
        for key, val in vals:
            self.input(key, val)
        return self
