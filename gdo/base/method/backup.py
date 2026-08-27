from gdo.base.Application import Application
from gdo.base.Backup import Backup
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Path import GDT_Path
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.mail.GDT_Email import GDT_Email


class backup(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_fields(
            GDT_Path('to').existing_dir().writable(),
            GDT_Email('email'),
            GDT_Bool('delete_after_mail').initial('1'),
        )
        super().gdo_create_form(form)

    def form_submitted(self):
        archive = Backup(
            Application.file_path('protected/config.toml'),
            Application.file_path(Application.config('dir.files')),
            {
                'host': Application.config('db.host'),
                'port': Application.config('db.port'),
                'name': Application.config('db.name'),
                'user': Application.config('db.user'),
                'pass': Application.config('db.pass'),
            },
        ).archive(self.param_value('to'))
        email = self.param_val('email')
        if not email:
            return self.msg('msg_backup_completed', (archive.name,))
        Backup.mail(archive, email)
        if self.param_val('delete_after_mail') == '1':
            archive.unlink()
            return self.msg('msg_backup_mailed_deleted', (email,))
        return self.msg('msg_backup_mailed', (archive.name, email))
