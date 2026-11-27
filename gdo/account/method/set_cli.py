from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Render import Render
from gdo.core import GDT_Field
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.core.GDT_Select import GDT_Select
from gdo.core.WithObject import WithObject
from gdo.date.GDT_Date import GDT_Date


class set_cli(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'set'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_UserSetting('name').positional(),
            GDT_String('value').positional(),
        ]

    def gdo_execute(self) -> GDT:
        user = self._env_user
        setting = self.param_value('name')
        if setting is None:
            from gdo.account.method.list_cli import list_cli
            return list_cli.gdo_execute(self)
        key = setting.get_name()
        value = self.param_val('value')
        gdt = GDO_UserSetting.setting_column(key, user)
        mode = self._env_mode

        if not value:
            tooltip = ''
            if gdt.has_tooltip():
                tooltip = f" ({gdt.get_tooltip_text()})"
            return self.reply('msg_print_cli_setting', (gdt.get_name(), Render.italic(gdt.render_val(), mode), tooltip, gdt.render_suggestion()))
        else:
            if gdt.is_writable():
                gdt.reset_error()
                if isinstance(gdt, GDT_Date) and not gdt.filter_date(value):
                    return self.err('err_cli_invalid_date')
                old = gdt.render_val()
                old_value = gdt.get_val()
                is_object = isinstance(gdt, WithObject)
                if is_object:
                    # Object validation resolves the field's current value,
                    # not the argument passed to validate().
                    gdt.val(value)
                valid = gdt.validate(value)
                if valid and is_object and gdt.get_value() is None:
                    gdt.error('err_invalid_choice_no_suggestions')
                    valid = False
                if not valid:
                    error = gdt.render_error()
                    if is_object:
                        gdt.val(old_value)
                    return self.err('err_param', (key, error))
                if isinstance(gdt, GDT_Select):
                    value = gdt.to_val(gdt.get_value())
                if is_object:
                    gdt.val(old_value)
                user.save_setting(key, value)
                if is_object:
                    gdt.val(value)
                new = user.get_setting_val(key)
                return self.reply('msg_set_cli_setting', (key, Render.italic(old, mode), Render.italic(new, mode)))
            else:
                return self.err('err_not_writable')
