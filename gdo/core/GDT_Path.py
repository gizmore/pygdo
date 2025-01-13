from gdo.base.Application import Application
from gdo.base.Util import Files, html, dump
from gdo.core.GDT_String import GDT_String


class GDT_Path(GDT_String):
    _path_existing: bool
    _path_is_dir: bool
    _path_is_file: bool

    def __init__(self, name):
        super().__init__(name)
        self._path_existing = False
        self._path_writable_dir = False
        self._path_writable_file = False
        self._path_is_dir = False
        self._path_is_file = False

    def existing(self, existing: bool = True):
        self._path_existing = existing
        return self.not_null()

    def existing_dir(self, existing: bool = True):
        self._path_is_dir = existing
        return self.existing()

    def existing_file(self, existing: bool = True):
        self._path_is_file = existing
        return self.existing()

    ############
    # Validate #
    ############
    def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
            return False

        if value is None:
            return True

        value = Application.file_path(value.lstrip('/'))
        if self._path_existing:
            if not Files.exists(value):
                self.error('err_path_not_exists', [html(value)])
                return False

        if self._path_is_file:
            if not Files.is_file(value):
                return self.error('err_path_not_file', [html(value)])

        if self._path_is_dir:
            if not Files.is_dir(value):
                return self.error('err_path_not_dir', [html(value)])

        return True
