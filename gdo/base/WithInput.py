class WithInput:

    _input: dict

    def input(self, key, val):
        if not hasattr(self, '_input'):
            self._input = {}
        self._input[key] = val
        return self

    def inputs(self, vals: dict):
        for key, val in vals.items():
            self.input(key, val)
        return self

    def has_input(self, key):
        return key in self._input.keys()

