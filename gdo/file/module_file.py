from gdo.base.GDO_Module import GDO_Module


class module_file(GDO_Module):

    def gdo_classes(self):
        return [
            GDO_File,
        ]