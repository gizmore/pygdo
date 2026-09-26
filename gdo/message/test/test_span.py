import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.message.GDT_HTML import GDT_HTML
from gdo.message.GDT_PRE import GDT_PRE


class SpanTest(GDOTestCase):

    def test_pre_renders_its_child_without_recursing(self):
        pre = GDT_PRE().add_field(GDT_HTML().html('Language README'))
        self.assertEqual('<pre>Language README</pre>', pre.render_html())


if __name__ == '__main__':
    unittest.main()
