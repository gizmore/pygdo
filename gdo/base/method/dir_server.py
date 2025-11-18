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
from os import walk

from gdo.ui.GDT_Icon import GDT_Icon
from gdo.ui.GDT_Link import GDT_Link


class dir_server(MethodTable):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

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
            files.append(GDO_File.blank({
                'file_name': dir_name,
                'file_size': Files.dir_size_recursive(dir_path),
                'file_mime': t('directory'),
            }))
        for file_name in sorted(filenames):
            file_path = f"{root}/{file_name}"
            files.append(GDO_File.blank({
                'file_name': file_name,
                'file_size': Files.size(file_path),
                'file_mime': Files.mime(file_path),
            }))
        return ResultArray(files, self.gdo_table())

    def render_file_name(self, gdt: GDT, gdo: GDO):
        return GDT_Link().href("/"+self.get_path()+"/"+gdt.get_val()).text_raw(gdt.get_val()).render(Mode.html)

    def render_file_icon(self, gdt: GDT_Icon, gdo: GDO_File):
        path = self.get_dir() + "/" + gdo.get_name()
        if Files.is_dir(path):
            icon = 'folder'
        else:
            map = {
                'text/plain': 'file',
            }
            icon = map.get(gdo.get_mime(), 'file')
        return gdt.icon_name(icon).render(Mode.cell)
