from gdo.base.util.href import href
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.file.GDT_File import GDT_File
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.core.GDT_String import GDT_String


class seo_add(MethodForm):
    """Publish an uploaded file under one stable, public SEO path."""

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'staff'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_fields(
            GDT_String('url').ascii().maxlen(255).not_null(),
            GDT_File('file').not_null(),
        )
        super().gdo_create_form(form)

    def form_submitted(self):
        file = self.param_value('file')[0]
        file.save()
        url = self.param_val('url').strip('/')
        GDO_SeoFile.blank({'sf_url': url, 'sf_file': file.get_id()}).insert()
        return self.redirect(href('file', 'seo_files'), 'msg_seo_file_added')
