from gdo.base.GDT import GDT
from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_UInt import GDT_UInt
from gdo.file.GDT_File import GDT_File
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.file.MethodFile import MethodFile


class preview_session(MethodFile):

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_String('gdt_name').not_null(),
            GDT_UInt('gdt_index'),
        ]

    def get_file(self) -> GDO_File:
        return self.param_value('file')

    def gdo_execute(self):
        file = GDT_File(self.param_value('gdt_name'))
        index = self.param_value('gdt_index')
        file = file.get_initial_files()[index]
        return GDT_FileOut().path(file.get_path())
