from gdo.base.Util import dump


class WithInput:
    """
    Add arguments array to a GDT.
    """
    _args: list
    _files: dict[str, tuple]

    def inputs(self, inputs: dict):
        for key, val in inputs.items():
            if isinstance(val, list):
                self.arg(f"--{key}")
                for v in val:
                    self.arg(v)
            else:
                dump(val)
                self.input(key, val)
        return self

    def input(self, key: str, val: str):
        self.arg(f"--{key}")
        self.arg(val)
        return self

    def arg(self, arg: str):
        self._args.append(arg)
        return self

    def args_copy(self, method):
        for arg in method._args:
            self.arg(arg)
        if hasattr(method, '_files'):
            self._files = method._files
        return self

    #########
    # Files #
    #########

    def add_file(self, key: str, filename: str, data: bytes):
        if not hasattr(self, '_files'):
            self._files = {}
        self._files[key] = (key, filename, data)

    def get_files(self, key: str):
        if not hasattr(self, '_files'):
            return []
        if key not in self._files:
            return []
        return [self._files[key]]
