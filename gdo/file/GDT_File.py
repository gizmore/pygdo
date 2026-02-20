from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.base.Util import Files, urlencode, html
from gdo.base.util.href import href
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
    _method: Method|None
    _display_only: bool

    def __init__(self, name: str):
        super().__init__(name)
        self.icon('file')
        self.label('file')
        self.table(GDO_File.table())
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
        self._method = None
        self._display_only = False

    def gdo_added_to_form(self, form: 'GDT_Form'):
        form.multipart()
        self._method = form._method
        self.upload_path(f"{form._method.gdo_module().get_name}.{form._method.get_name()}.{self._name}")

    def get_file(self) -> list[GDO_File]:
        return self.get_value()

    ###########
    # Options #
    ###########
    def display_only(self, display_only: bool = True):
        self._display_only = display_only
        return self

    def upload_path(self, path: str):
        self._upload_path = path.strip('/')
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
        return self.get_initial_files()

    def to_val(self, value) -> str:
        return None if value is None else value[0].get_id()

    def to_value(self, val: str):
        if value := super().to_value(val):
            return [value]
        return None

    def get_initial_files(self):
        if not Application.has_session():
            return []
        dir = self.get_temp_dir()
        if not Files.is_dir(dir):
            return self.get_persisted_files()
        if file := GDO_File.from_dir(dir):
            return [file] + self.get_persisted_files()
        return self.get_persisted_files()


    def get_persisted_files(self) -> list[GDO_File] | None:
        return super().get_value() or []

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
        self.deletion(method)

    def deletion(self, method: Method):
        if f"{self._name}.sess.delete" in method._raw_args.args:
            self.cleanup_temp_dir()
        if f"{self._name}.file.delete" in method._raw_args.args:
            if files := self.get_persisted_files():
                for file in files:
                    file.delete()
            self.val(None)

    def get_temp_dir(self):
        sessid = Application.get_session().get_id() if Application.has_session() else '0'
        files_dir = Application.config('file.directory')
        return Application.temp_path(f"{files_dir}{self._upload_path}/{sessid}/")

    ############
    # Validate #
    ############
    def validate(self, val: str|None) -> bool:
        # if self._method:
        #     self.gdo_file_upload(self._method)
        files = self.get_initial_files() or self.to_value(val)
        if not files:
            return super().validate(None)
        if self._multiple:
            if not self.validate_files(files):
                return False
            # for file in files:
            #     file.save()
            #     self.val(file.get_id())
        else:
            if not self.validate_file(files[0]):
                return False
            files[0].save()
            self.val(files[0].get_id())
        self.cleanup_temp_dir()
        return True

    def validate_files(self, value: any) -> bool:
        for file in value:
            if not self.validate_file(file):
                return False
        return True

    def validate_file(self, file: GDO_File):
        if not self.validate_mime(file):
            return self.error_mime(file)
        if self._min_len and file.get_size() < self._min_len:
            return self.error_min_size()
        if self._max_len and file.get_size() > self._max_len:
            return self.error_max_size()
        return True

    def validate_mime(self, file: GDO_File):
        if not self._mimes:
            return True
        if file.get_mime() not in self._mimes:
            return False
        return True

    def error_mime(self, file: GDO_File):
        return self.error('err_upload_mime', (file.get_mime(),))

    def error_min_size(self):
        return self.error('err_upload_min_size', (Files.human_file_size(self._min_len),))

    def error_max_size(self):
        return self.error('err_upload_max_size', (Files.human_file_size(self._max_len),))

    ##########
    # Render #
    ##########
    def href_preview(self, file: GDO_File) -> str:
        if file.is_persisted():
            return file.get_preview_href()
        else:
            append = '&path=' + urlencode(self._upload_path) + "&token=" + file.gdo_hash()
            return href('file', 'preview_session', append)

    def html_capture(self) -> str:
        return '' if self._no_capture else ' capture=capture'

    def render_form(self) -> str:
        return GDT_Template().template('file', 'test.html', {'field': self}).render()

    def display_val(cls, val: str) -> str:
        if val and (file := GDO_File.table().get_by_aid(val)):
            return html(file.get_name())
        return t('none')

    ###########
    # Cleanup #
    ###########

    def cleanup_temp_dir(self):
        Files.delete_dir(self.get_temp_dir())

    def cleanup_temp_files(self, files: list[GDO_File]):
        for file in files:
            self.cleanup_temp_file(file)

    def cleanup_temp_file(self, file: GDO_File):
        path = file.get_path()
        dir = Files.dirname(path)
        Files.delete_dir(dir)


    ##########
    # Upload #
    ##########
    def flow_upload(self):
        return GDT_String('result')
