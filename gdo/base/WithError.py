class WithError:
    _errkey: str
    _errargs: list

    def has_error(self) -> bool:
        return hasattr(self, '_errkey')

    def error_raw(self, error_message: str):
        return self.error('%s', [error_message])

    def error(self, key: str, args: list = None):
        self._errkey = key
        self._errargs = args
        return self

