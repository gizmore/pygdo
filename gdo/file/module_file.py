from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDO_File import GDO_File


class module_file(GDO_Module):

    def gdo_classes(self):
        return [
            GDO_File,
        ]
    