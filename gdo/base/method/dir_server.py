from gdo.base.Application import Application
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Render import Mode
from gdo.base.Result import Result
from gdo.base.ResultArray import ResultArray
from gdo.base.Trans import t
from gdo.base.Util import Files
from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_Path import GDT_Path
from gdo.table.MethodTable import MethodTable
import os
from os import walk
from urllib.parse import unquote

from gdo.ui.GDT_Icon import GDT_Icon
from gdo.ui.GDT_Link import GDT_Link


class dir_server(MethodTable):

    def gdo_needs_authentication(self) -> bool:
        return False

    @staticmethod
    def is_forbidden(url: str) -> bool:
        url = unquote(url).lstrip('/')
        if '\\' in url or any(part in ('.', '..') for part in url.split('/')):
            return True
        root = os.path.realpath(Application.file_path())
        target = os.path.realpath(os.path.join(root, url))
        try:
            if os.path.commonpath((root, target)) != root:
                return True
            for name in ('temp', 'protected'):
                private = os.path.realpath(os.path.join(root, name))
                if os.path.commonpath((private, target)) == private:
                    return True
        except ValueError:
            return True
        return False

    def gdo_execute(self) -> GDT:
        if self.is_forbidden(self.param_val('_url')):
            Application.status('403 Forbidden')
            return self.err('err_file_forbidden')
        return super().gdo_execute()

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_page_positional(self) -> bool:
        return False

    def gdo_table(self) -> GDO:
        return GDO_File.table()

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Path('_url').existing_dir(),
        ]

    def get_path(self) -> str:
        return self.param_value('_url').lstrip('/')

    def get_dir(self) -> str:
        return Application.file_path(self.get_path())

    def gdo_table_headers(self) -> list[GDT]:
        t = self.gdo_table()
        return [
            GDT_Icon('file_icon'),
            t.column('file_name'),
            t.column('file_mime'),
            t.column('file_size'),
        ]

    def gdo_table_result(self) -> Result:
        root = self.get_dir()
        for (dirpath, dirnames, filenames) in walk(root):
            break

        files = []
        for dir_name in sorted(dirnames):
            dir_path = f"{root}/{dir_name}"
            if os.path.islink(dir_path) or self.is_forbidden(f"{self.get_path()}/{dir_name}"):
                continue
            files.append(GDO_File.blank({
                'file_name': dir_name,
                'file_size': Files.dir_size_recursive(dir_path),
                'file_mime': t('directory'),
            }))
        for file_name in sorted(filenames):
            file_path = f"{root}/{file_name}"
            if os.path.islink(file_path) or self.is_forbidden(f"{self.get_path()}/{file_name}"):
                continue
            files.append(GDO_File.blank({
                'file_name': file_name,
                'file_size': Files.size(file_path),
                'file_mime': Files.mime(file_path),
            }))
        return ResultArray(files, self.gdo_table())

    def gdo_table_sort_result(self, result: list[GDO]) -> list[GDO]:
        """Keep directories above files while preserving the selected sort."""
        root = self.get_dir()
        return sorted(result, key=lambda file: not Files.is_dir(f"{root}/{file.get_name()}"))

    def render_file_name(self, gdt: GDT, gdo: GDO):
        path = self.get_path().rstrip('/')
        return GDT_Link().href("/" + path + "/" + gdt.get_val()).text_raw(gdt.get_val()).render(Mode.render_html)

    def render_file_icon(self, gdt: GDT_Icon, gdo: GDO_File):
        path = self.get_dir() + "/" + gdo.get_name()
        if Files.is_dir(path):
            icon = 'folder'
        else:
            map = {
                'text/plain': 'file',
            }
            icon = map.get(gdo.get_mime(), 'file')
        return gdt.icon_name(icon).render(Mode.render_cell)
