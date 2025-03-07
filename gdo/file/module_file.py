from gdo.base.GDO_Module import GDO_Module
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.ui.GDT_Page import GDT_Page


class module_file(GDO_Module):

    def gdo_classes(self):
        from gdo.core.GDO_File import GDO_File
        return [
            GDO_File,
            GDO_SeoFile,
        ]

    def gdo_load_scripts(self, page: 'GDT_Page'):
        self.add_bower_js('flow.js/lib/flow.js')
