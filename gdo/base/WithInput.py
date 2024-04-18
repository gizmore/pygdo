from gdo.base.Util import err


class WithInput:
    _input: dict

    def input(self, key, val):
        self._input[key] = val
        # err(f'set {key} to {val}')
        return self

    def inputs(self, vals: dict):
        if not hasattr(self, '_input'):
            self._input = {}
        for key, val in vals.items():
            self.input(key, val)
        return self

    def has_input(self, key):
        return key in self._input.keys()

