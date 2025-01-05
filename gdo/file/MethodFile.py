from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Util import dump
from gdo.core.GDO_File import GDO_File
from gdo.file.GDT_FileOut import GDT_FileOut


class MethodFile(Method):
    """
    A method that renders a raw file.
    """

    def render_file(self, file: GDO_File) -> GDT:
        Application.header('Content-Type', file.get_mime())
        Application.header('Content-Length', str(file.get_size()))
        Application.header('Content-Disposition', f'inline; filename="{file.get_name()}"')
        return GDT_FileOut().path(file.get_path())
