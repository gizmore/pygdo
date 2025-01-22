from gdo.base.Trans import t


class WithError:
    _errkey: str
    _errargs: tuple

    def has_error(self) -> bool:
        return hasattr(self, '_errkey')

    def error_raw(self, error_message: str):
        return self.error('%s', (error_message,))

    def render_error(self) -> str:
        return t(self._errkey, self._errargs)

    def error(self, key: str, args: tuple = None):
        self._errkey = key
        self._errargs = args
        return self

    def reset_error(self):
        delattr(self, '_errkey') if hasattr(self, '_errkey') else None
        delattr(self, '_errargs') if hasattr(self, '_errargs') else None
        return self


