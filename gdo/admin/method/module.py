from gdo.admin.GDT_Module import GDT_Module
from gdo.admin.method.configure import configure
from gdo.admin.method.install import install
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Trans import sitename
from gdo.base.Util import Files
from gdo.base.util.href import href
from gdo.core.GDT_Container import GDT_Container
from gdo.message.GDT_HTML import GDT_HTML
from gdo.message.GDT_PRE import GDT_PRE
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Menu import GDT_Menu
from gdo.ui.GDT_Panel import GDT_Panel


class module(Method):

    def gdo_connectors(self) -> str:
        return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Module('module').not_null(),
        ]

    async def submethod(self, klass: type[Method]):
        method = klass().args_copy(self).env_copy(self)
        return await method.execute()

    def get_module(self) -> GDO_Module:
        return self.param_value('module')

    def gdo_render_descr(self) -> str:
        m = self.get_module()
        return self.t('md_admin_module', (m.render_name(), sitename()))

    def gdo_render_title(self) -> str:
        m = self.get_module()
        return self.t('mt_admin_module', (m.render_name(),))

    def render_module_list(self, names: list) -> str:
        loader = ModuleLoader.instance()
        rendered = []
        for name in names:
            dependency = loader.load_module_db(name) or loader.load_module_fs(name)
            label = (GDT_Link().
                     text_raw(name).
                     href(href('admin', 'module', f'&module={name}')).
                     attr('style', 'color: inherit').
                     render())
            rendered.append(
                Render.green(label) if dependency and dependency.installed() else Render.red(label)
            )
        return ', '.join(rendered) if rendered else '---'

    def module_relations(self) -> GDT_Container:
        module = self.get_module()
        return GDT_Container().vertical().add_fields(
            GDT_Panel().title('dependencies').text_raw(self.render_module_list(module.gdo_dependencies()), escaped=False),
            GDT_Panel().title('friendencies').text_raw(self.render_module_list(module.gdo_friendencies()), escaped=False),
        )

    def module_readme(self) -> GDT_PRE:
        module = self.get_module()
        path = module.file_path('README.md')
        readme = Files.get_contents(path) if Files.is_file(path) else ''
        descriptions = '\n'
        for method in module.get_methods():
            # A method may render its title from the same parameters as this
            # module view (notably admin.module itself).
            method.args_copy(self)
            descriptions += f'{method.gdo_render_simple_title()}: {method.gdo_render_simple_descr()}\n'
        return GDT_PRE().add_field(GDT_HTML().html(readme + descriptions))

    async def gdo_execute(self) -> GDT:
        return GDT_Container().vertical().add_fields(
            GDT_Menu().add_fields(*self.get_module().gdo_admin_links()),
            self.module_readme(),
            self.module_relations(),
            await self.submethod(install),
            await self.submethod(configure))
