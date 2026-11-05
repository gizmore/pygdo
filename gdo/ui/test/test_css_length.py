import unittest

from gdo.ui.GDT_CSSLength import GDT_CSSLength


class CSSLengthTest(unittest.TestCase):
    def test_css_pixel_and_percent_lengths_resolve_against_context(self):
        self.assertEqual(GDT_CSSLength.resolve('20px', 1920), 20)
        self.assertEqual(GDT_CSSLength.resolve('12.5%', 640), 80)
        self.assertEqual(GDT_CSSLength.resolve('-5px', 640), -5)
        for invalid in ('auto', '30em', 'nanpx', '10', 'calc(2px)', ''):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                GDT_CSSLength.resolve(invalid, 640)
