from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Trans import t
from gdo.base.util.href import href
from gdo.core.GDO_User import GDO_User
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.GDT_Field import GDT_Field
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_User import GDT_User
from gdo.core.GDT_UserSetting import GDT_UserSetting
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.ui.GDT_Divider import GDT_Divider
from gdo.ui.GDT_Link import GDT_Link


class edit_user(MethodForm):
    """Let staff edit every stored setting of a selected user."""

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_User('user')]

    def get_user(self) -> GDO_User | None:
        return self.param_value('user', False)

    def gdo_render_title(self) -> str:
        if user := self.get_user():
            return t('mt_admin_edit_user_for', (user.render_name(),))
        return t('mt_admin_edit_user')

    def setting_fields(self) -> list[GDT_Field]:
        if hasattr(self, '_setting_fields'):
            return self._setting_fields
        user = self.get_user()
        if user is None:
            return []
        ModuleLoader.instance().init_user_settings()
        GDO_UserSetting.load_for_user(user)
        fields = []
        for key, template in sorted(GDT_UserSetting.KNOWN.items()):
            # User-config links are actions, not stored configuration values.
            if not isinstance(template, GDT_Field) or isinstance(template, GDT_Link):
                continue
            fields.append(template.copy_as(key).hidden(False).writable(True).val(user._vals.get(key)))
        self._setting_fields = fields
        return fields

    def grouped_setting_fields(self) -> list[GDT]:
        """Interleave the selected user's settings with their owning modules."""
        if hasattr(self, '_grouped_setting_fields'):
            return self._grouped_setting_fields
        fields = {field.get_name(): field for field in self.setting_fields()}
        grouped = []
        loader = ModuleLoader.instance()
        for _name, module in sorted(loader._cache.items()):
            names = []
            for template in [*module.gdo_user_config(), *module.gdo_user_settings()]:
                if isinstance(template, GDT_Field) and not isinstance(template, GDT_Link):
                    names.append(template.get_name())
            module_fields = [fields.pop(name) for name in names if name in fields]
            if module_fields:
                grouped.append(GDT_Divider().title_raw(module.render_name()))
                grouped.extend(module_fields)
        # Do not silently lose a registered setting if its module could not
        # be resolved (for example after an interrupted module reload).
        if fields:
            grouped.append(GDT_Divider().title_raw('Other'))
            grouped.extend(fields.values())
        self._grouped_setting_fields = grouped
        return grouped

    def gdo_create_form(self, form: GDT_Form) -> None:
        if self.get_user() is None:
            form.text('md_admin_edit_user')
            form.add_field(GDT_User('select_user').not_null().with_completion())
        else:
            form.text('md_admin_edit_user_for', (self.get_user().render_name(),))
            form.add_fields(*self.grouped_setting_fields())
        super().gdo_create_form(form)

    @staticmethod
    def setting_changed(field: GDT_Field, old, new) -> bool:
        """Compare browser datetime-local input at its millisecond precision.

        Databases retain microseconds while HTML datetime-local fields only
        submit milliseconds.  Re-posting an unchanged value must therefore
        not create a spurious settings update or discard the stored tail.
        """
        if isinstance(field, GDT_Password) and not new:
            return False
        if isinstance(field, GDT_Timestamp):
            old = field.milliseconds(old)
            new = field.milliseconds(new)
        return old != new

    def form_submitted(self):
        if self.get_user() is None:
            user = self.param_value('select_user')
            return self.redirect(href('admin', 'edit_user', f'&user={user.get_id()}'))

        user = self.get_user()
        changes = []
        for field in self.setting_fields():
            old = field.get_prev()
            new = field.get_val()
            if self.setting_changed(field, old, new):
                user.save_setting(field.get_name(), new)
                changes.append('%s: %s → %s' % (
                    field.render_label(),
                    Render.italic(field.display_var(old), self._env_mode),
                    Render.italic(field.display_var(new), self._env_mode),
                ))
        if changes:
            self.msg('msg_admin_user_settings_changed', (user.render_name(), ' '.join(changes)))
        return self.render_page()
