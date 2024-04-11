import os.path
import unittest

from gdo.core.Application import Application
from gdo.core.Util import Strings, Arrays


class UtilityTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../"))
        return self

    def test_strings(self):
        s = "foo.bar.html"
        self.assertEqual(Strings.substr_from(s, '.'), 'bar.html', 'Test substr_from')
        self.assertEqual(Strings.substr_to(s, '.'), 'foo', 'Test substr_to')
        self.assertEqual(Strings.rsubstr_from(s, '.'), 'html', 'Test rsubstr_from')
        self.assertEqual(Strings.rsubstr_to(s, '.'), 'foo.bar', 'Test rsubstr_to')

    def test_arrays(self):
        original_list = [1, 2, 3, 4, 2, 3, 5]
        expected_unique_list = [1, 2, 3, 4, 5]
        unique_list = Arrays.unique(original_list)
        self.assertEqual(unique_list, expected_unique_list, 'Test unique')


if __name__ == '__main__':
    unittest.main()
