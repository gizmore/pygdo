from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting


class set_cli(Method):

    def gdo_trigger(self) -> str:
        return 'set'

    def gdo_parameters(self) -> [GDT]:
        return [
            GDT_UserSetting('name').not_null(),
            GDT_String('value').positional(),
        ]

    def gdo_execute(self):
        user = self._env_user
        key = self.param_val('name')
        value = self.param_val('value')
        gdt = GDO_UserSetting.setting_column(key, user)
        mode = self._env_mode

        if not value:
            tooltip = ''
            if gdt.has_tooltip():
                tooltip = f" ({gdt.get_tooltip_text()})"
            return self.reply('msg_print_cli_setting', [gdt.get_name(), Render.italic(gdt.render_var(), mode), tooltip, gdt.render_suggestion()])
        else:
            gdt = GDO_UserSetting.setting_column(key, user)
            old = gdt.render_var()
            user.save_setting(key, value)
            new = user.get_setting_val(key)
            return self.reply('msg_set_cli_setting', [key, Render.italic(old, mode), Render.italic(new, mode)])

