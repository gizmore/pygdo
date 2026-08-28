import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.language.GDT_Language import GDT_Language


class LanguageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Application.init(os.path.dirname(__file__ + '/../../../../'))
        Application.init_cli()
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)

    def test_iso_primary_key_resolves(self):
        for iso in ('en', 'de'):
            with self.subTest(iso=iso):
                field = GDT_Language('language').supported().not_null().val(iso)
                self.assertTrue(field.validate(field.get_val()))
                self.assertEqual(iso, field.get_value().get_id())

    def test_cell_renders_localized_language_name(self):
        field = GDT_Language('language').supported().val('de')
        self.assertEqual(t('l_de'), field.render_cell())
        self.assertEqual(t('l_de'), field.render_txt())
        self.assertEqual(t('l_de'), field.render_cli())


if __name__ == '__main__':
    unittest.main()
