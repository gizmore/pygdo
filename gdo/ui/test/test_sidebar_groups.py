import unittest
from unittest.mock import MagicMock, patch

from gdo.ui.GDT_Bar import GDT_Bar
from gdo.ui.GDT_Page import GDT_Page


class SidebarGroupsTest(unittest.TestCase):
    def test_entries_from_one_module_share_a_group(self):
        page = GDT_Page()
        page._left_bar = GDT_Bar('left')

        def add_entries(count):
            def add(page):
                for _ in range(count):
                    field = MagicMock()
                    field.render_html.return_value = '<a>Link</a>'
                    page._left_bar.add_field(field)
            return add

        modules = [MagicMock(gdo_init_sidebar=add_entries(count)) for count in (1, 3, 0, 1)]
        with patch('gdo.ui.GDT_Page.ModuleLoader.instance') as loader:
            loader.return_value.enabled.return_value = modules
            page.init_sidebars()

        self.assertEqual({0, 1, 4}, page._left_bar._group_starts)
        rows = page._left_bar.render_bar_fields().splitlines()
        self.assertIn('gdt-bar-group-start', rows[1])
        self.assertNotIn('gdt-bar-group-start', rows[2])
        self.assertNotIn('gdt-bar-group-start', rows[3])
        self.assertIn('gdt-bar-group-start', rows[4])
