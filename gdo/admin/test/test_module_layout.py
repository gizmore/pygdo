import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from gdo.admin.method.module import module
from gdo.base.Application import Application


class ModuleLayoutTest(unittest.IsolatedAsyncioTestCase):
    async def test_forms_precede_module_documentation(self):
        with patch.object(Application, 'get_mode', return_value=None):
            page = module()
        page.get_module = MagicMock()
        page.get_module.return_value.gdo_admin_links.return_value = []
        page.submethod = AsyncMock(side_effect=['install form', 'configuration form'])
        page.module_relations = MagicMock(return_value='dependencies')
        page.module_readme = MagicMock(return_value='documentation')
        container = MagicMock()
        container.vertical.return_value = container
        menu = MagicMock()
        menu.add_fields.return_value = 'menu'
        with patch('gdo.admin.method.module.GDT_Container', return_value=container), \
             patch('gdo.admin.method.module.GDT_Menu', return_value=menu):
            await page.gdo_execute()
        container.add_fields.assert_called_once_with('menu', 'install form', 'configuration form',
                                                     'dependencies', 'documentation')
