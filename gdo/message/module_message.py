from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.message.editor.EditorHTML import EditorHTML
from gdo.message.editor.GDT_Editor import GDT_Editor


class module_message(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 23

    def gdo_init(self):
        GDT_Editor.register(EditorHTML)

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Editor('default_editor').not_null().initial('html'),
        ]

    def gdo_user_settings(self) -> list[GDT]:
        return [
            GDT_Editor('message_editor').not_null().initial('html'),
        ]
