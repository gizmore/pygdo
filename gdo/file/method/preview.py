from gdo.base.GDT import GDT
from gdo.core.GDO_File import GDO_File
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_Token import GDT_Token
from gdo.core.GDT_UInt import GDT_UInt
from gdo.file.GDT_File import GDT_File
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.file.MethodFile import MethodFile


class preview(MethodFile):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_File('file').not_null(),
            GDT_Token('token').not_null(),
        ]

    def get_file(self) -> GDO_File:
        return self.param_value('file')

    def gdo_execute(self) -> GDT:
        file = self.get_file()
        token = self.param_val('token')
        if token != file.gdo_hash():
            return self.err('err_token')

        return self.render_file(file)
