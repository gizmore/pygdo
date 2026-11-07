import unittest

from gdo.core.GDT_Enum import GDT_Enum
from gdo.shadowdogs.GDT_Race import GDT_Race
from gdo.video.method.duckanim import duckanim


class SelectErrorHintTest(unittest.TestCase):
    def test_default_and_opt_in_limit(self):
        field = GDT_Enum('choice').choices({f'key{i}': str(i) for i in range(52)})
        self.assertEqual('key0, key1, key2, key3, key4, ...', field.render_suggestion())
        self.assertIs(field, field.errorhint_all())
        hints = field.render_suggestion().split(', ')
        self.assertEqual(51, len(hints))
        self.assertEqual('key49', hints[-2])
        self.assertEqual('...', hints[-1])
        self.assertNotIn('key50', hints)
        self.assertEqual(6, len(field.errorhint_all(False).render_suggestion().split(', ')))

    def test_duck_and_player_race_expose_all_keys(self):
        from gdo.base.Application import Application
        from gdo.base.Render import Mode
        Application.mode(Mode.render_cli)
        self.assertIn('plz', duckanim().gdo_parameters()[0].render_suggestion())
        race_hint = GDT_Race('race').not_null().render_suggestion()
        self.assertIn('troll', race_hint)
        self.assertNotIn('dragon', race_hint)
        self.assertNotIn('...', race_hint)
