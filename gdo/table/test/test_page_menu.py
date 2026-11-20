import unittest
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.table.GDT_PageMenu import GDT_PageMenu


class PageMenuTest(unittest.TestCase):
    def test_empty_and_single_page_have_no_html(self):
        method = MagicMock()
        method.get_page_num.return_value = 1
        method.gdo_paginate_size.return_value = 10
        with patch.object(Application, 'get_mode', return_value=None):
            for total in (0, 1, 10):
                with self.subTest(total=total):
                    method.get_num_results.return_value = total
                    self.assertEqual('', GDT_PageMenu('pages').paginate(method).render_html())

    def test_multiple_pages_render_template(self):
        method = MagicMock()
        method.get_page_num.return_value = 1
        method.gdo_paginate_size.return_value = 10
        method.get_num_results.return_value = 11
        with patch.object(Application, 'get_mode', return_value=None), \
             patch('gdo.table.GDT_PageMenu.GDT_Template') as template:
            template.return_value.template.return_value.render_html.return_value = 'pagination'
            self.assertEqual('pagination', GDT_PageMenu('pages').paginate(method).render_html())
