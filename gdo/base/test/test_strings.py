import unittest
from gdotest.TestUtil import GDOTestCase

from gdo.base.Util import Strings, StringsUtil


class StringsTest(GDOTestCase):

    def test_seo_keeps_ascii_alnum_and_collapses_punctuation(self):
        self.assertEqual('Hello_world_42', Strings.seo('Hello, world!!! 42'))
        self.assertEqual('one_two', Strings.seo('one___two'))

    def test_seo_replaces_non_ascii_characters(self):
        self.assertEqual('H_llo', Strings.seo('Hällo'))

    def test_utf8_obfuscate_avoids_ascii_nickname_matches(self):
        self.assertEqual('rау', StringsUtil.utf8obfuscate('ray'))
        self.assertEqual('ray', StringsUtil.utf8deobfuscate('rау'))
