import unittest
from unittest.mock import MagicMock, patch

from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Page import GDT_Page


class SidebarGroupsTest(unittest.TestCase):
    def test_entries_from_one_module_share_a_group(self):
        page = GDT_Page()
        page._left_bar = GDT_Bar('left')
        page._right_bar = GDT_Bar('right')

        def add_entries(count):
            def add(page):
                for _ in range(count):
                    field = MagicMock()
                    field.render_html.return_value = '<a>Link</a>'
                    page._left_bar.add_field(field)
                    page._right_bar.add_field(field)
            return add

        modules = [MagicMock(gdo_init_sidebar=add_entries(count)) for count in (1, 3, 0, 1)]
        for module in modules:
            module._priority = 50
        with patch('gdo.ui.GDT_Page.ModuleLoader.instance') as loader:
            loader.return_value.enabled.return_value = modules
            page.init_sidebars()

        self.assertEqual({0, 1, 4}, page._left_bar._group_starts)
        rows = page._left_bar.render_bar_fields().splitlines()
        self.assertIn('gdt-bar-group-start', rows[1])
        self.assertNotIn('gdt-bar-group-start', rows[2])
        self.assertNotIn('gdt-bar-group-start', rows[3])
        self.assertIn('gdt-bar-group-start', rows[4])

        page._left_bar._active_module = modules[1].get_name
        rows = page._left_bar.render_bar_fields().splitlines()
        self.assertNotIn('gdo-active-module', rows[0])
        for row in rows[1:4]:
            self.assertIn('gdo-active-module', row)
        self.assertNotIn('gdo-active-module', rows[4])
        page._right_bar._active_module = modules[1].get_name
        self.assertEqual(rows, page._right_bar.render_bar_fields().splitlines())

    def test_sidebar_modules_are_sorted_by_descending_priority_stably(self):
        page = GDT_Page()
        page._left_bar = GDT_Bar('left')
        page._right_bar = GDT_Bar('right')
        order = []
        modules = []
        for name, priority in [('low', 10), ('site', 20000), ('same1', 50), ('same2', 50)]:
            module = MagicMock()
            module._priority = priority
            module.gdo_init_sidebar.side_effect = lambda _page, name=name: order.append(name)
            modules.append(module)
        with patch('gdo.ui.GDT_Page.ModuleLoader.instance') as loader:
            loader.return_value.enabled.return_value = modules
            page.init_sidebars()
        self.assertEqual(['site', 'same1', 'same2', 'low'], order)
