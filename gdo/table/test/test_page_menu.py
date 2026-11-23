import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gdo.base.Application import Application
from gdo.table.GDT_PageMenu import GDT_PageMenu
from gdo.core.GDT_Template import Templite


class PageMenuTest(unittest.TestCase):
    def test_cards_render_pagination_around_results(self):
        method = MagicMock()
        method.get_table_result.return_value = ['video']
        method.get_page_menu.return_value.render_html.return_value = '<nav>pages</nav>'
        method.render_gdo.return_value = '<article>video</article>'
        template = Templite(str(Path(__file__).resolve().parents[1] / 'tpl' / 'cards.html'), caching=False)
        rendered = template.render(method=method)
        self.assertEqual(2, rendered.count('<nav>pages</nav>'))
        self.assertLess(rendered.index('<nav>pages</nav>'), rendered.index('<article>'))
        self.assertLess(rendered.index('<article>'), rendered.rindex('<nav>pages</nav>'))

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
