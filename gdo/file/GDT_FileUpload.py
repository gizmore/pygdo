from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_Container import GDT_Container
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Template import GDT_Template
from gdo.file.GDT_MimeType import GDT_MimeType


class GDT_FileUpload(GDT_Container, GDT_Field):
    _mimes: dict[str, str]
    _min_len: int
    _max_len: int
    _min_dur: int
    _max_dur: int
    _no_delete: bool
    _no_capture: bool
    _image_file: bool

    def __init__(self, name: str):
        super().__init__(name)
        self._mimes = {}
        self._min_len = 0
        self._max_len = 0
        self._min_dur = 0
        self._max_dur = 0
        self._no_delete = False
        self._no_capture = False
        self._image_file = False

    ###########
    # Options #
    ###########

    def mimes(self, mimes: dict):
        self._mimes.update(mimes)
        return self

    def images(self):
        self._image_file = True
        return self.mimes(GDT_MimeType.IMAGE_TYPES)

    def minlen(self, min_len: int):
        self._min_len = min_len
        return self

    def maxlen(self, max_len: int):
        self._max_len = max_len
        return self

    def no_delete(self, no_delete: bool):
        self._no_delete = no_delete
        return self

    def no_capture(self, no_capture: bool):
        self._no_capture = no_capture
        return self

    #######
    # GDT #
    #######
    def get_initial_files(self) -> list[GDO_File]:
        return []

    ##########
    # Upload #
    ##########

    ############
    # Validate #
    ############
    def validate(self, val: str | None, value: any) -> bool:
        if value is None:
            return super().validate(val, value)
        return True

    ##########
    # Render #
    ##########
    def html_capture(self):
        return '' if self._no_capture else ' capture=capture'

    def render_form(self) -> str:
        return GDT_Template().template('File', 'file_upload.html', {'field': self}).render()
