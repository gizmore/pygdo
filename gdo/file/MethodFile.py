from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_File import GDO_File
from gdo.file.GDT_FileOut import GDT_FileOut


class MethodFile(Method):

    def render_file(self, file: GDO_File) -> GDT:
        return GDT_FileOut().path(file.get_target_path())
