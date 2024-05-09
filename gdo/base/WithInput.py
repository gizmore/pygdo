class WithInput:
    """
    Add arguments array to a GDT.
    """
    _args: list

    def inputs(self, inputs: dict):
        for key, val in inputs.items():
            if isinstance(val, list) and len(val) == 1:  # WSGI unwrap single object
                val = val[0]
            self.input(key, val)
        return self

    def input(self, key: str, val: str):
        self.arg(f"--{key}")
        return self.arg(val)

    def arg(self, arg: str):
        self._args.append(arg)
        return self

    def args_copy(self, method):
        self._args = method._args
        return self
