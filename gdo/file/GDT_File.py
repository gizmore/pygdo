import mimetypes

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.Util import Files
from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Template import GDT_Template
from gdo.file.GDT_MimeType import GDT_MimeType
from gdo.form.GDT_Form import GDT_Form


class GDT_File(GDT_Object):
    _upload_path: str
    _mimes: dict[str, str]
    _min_len: int
    _max_len: int
    _min_dur: int
    _max_dur: int
    _no_delete: bool
    _no_capture: bool
    _image_file: bool
    _preview: bool

    def __init__(self, name: str):
        super().__init__(name)
        self._upload_path = name
        self._mimes = {}
        self._min_len = 0
        self._max_len = 0
        self._min_dur = 0
        self._max_dur = 0
        self._no_delete = False
        self._no_capture = False
        self._image_file = False
        self._preview = True
        self.table(GDO_File.table())

    def gdo_added_to_form(self, form: 'GDT_Form'):
        form.multipart()

    ###########
    # Options #
    ###########
    def upload_path(self, path: str):
        self._upload_path = path
        return self

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
    def get_value(self):
        files = self.get_initial_files()
        if not files:
            return super().get_value() or []
        return files

    def get_initial_files(self):
        if not Application.has_session():
            return []
        dir = self.get_temp_dir()
        if not Files.is_dir(dir):
            return []
        if file := GDO_File.from_dir(dir):
            return [file]
        return []

    ##########
    # Upload #
    ##########
    def gdo_file_upload(self, method: Method):
        """
        Move file from memory to temp disk
        """
        if files_data := method.get_files(self.get_name()):
            for file_data in files_data:
                dir = self.get_temp_dir()
                Files.create_dir(dir)
                path = dir + "0"
                Files.put_contents(path, file_data[2])
                Files.put_contents(dir + "mime", Files.mime(path))
                Files.put_contents(dir + "name", file_data[1])

    def get_temp_dir(self):
        sessid = Application.get_session().get_id()
        files_dir = Application.config('file.directory')
        dir = Application.temp_path(f"{files_dir}{self._upload_path}/{sessid}/")
        return dir

    ############
    # Validate #
    ############
    def validate(self, val: str | None, value: any) -> bool:
        if not value:
            return super().validate(val, None)
        return self.validate_files(val, value)

    def validate_files(self, val: str | None, value: any) -> bool:
        for file in value:
            if not self.validate_file(file):
                return False
        return True

    def validate_file(self, file: GDO_File):
        if not self.validate_mime(file):
            return self.error_mime()
        return True

    def validate_mime(self, file: GDO_File):
        if not self._mimes:
            return True
        if file.get_mime() not in self._mimes:
            return False
        return True

    def error_mime(self):
        return self.error('err_upload_mime')

    ##########
    # Render #
    ##########
    def html_capture(self):
        return '' if self._no_capture else ' capture=capture'

    def render_form(self) -> str:
        return GDT_Template().template('file', 'test.html', {'field': self}).render()

    ##########
    # Upload #
    ##########
    def flow_upload(self):
        return GDT_String('result').val('test')
