from gdo.base.GDO_Module import GDO_Module
from gdo.message.editor.EditorHTML import EditorHTML
from gdo.message.editor.GDT_Editor import GDT_Editor


class module_message(GDO_Module):

    def gdo_init(self):
        GDT_Editor.register(EditorHTML)
