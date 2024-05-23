class WithInput:
    """
    Add arguments array to a GDT.
    """
    _args: list

    def inputs(self, inputs: dict):
        for key, val in inputs.items():
            if isinstance(val, list):
                self.arg(f"--{key}")
                for v in val:
                    self.arg(v)
                    # self.input(key, v)
            else:
                self.input(key, val)
            # if isinstance(val, list) and len(val) == 1:  # WSGI unwrap single object
            #     val = val[0]
            # self.input(key, val)
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
        # self._args = method._args
        return self
