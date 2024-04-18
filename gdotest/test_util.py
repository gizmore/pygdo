import os.path
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.base.Util import Strings, Arrays


class UtilityTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
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

    def test_array_walk(self):
        the_dict = {"db": {"mysql": {"host": "localhost"}}}
        val = Arrays.walk(the_dict, 'db.mysql.host')
        self.assertEqual('localhost', val, 'Arrays.walk does not work')
        val = Arrays.walk(the_dict, 'db.mysql.name')
        self.assertIsNone(val, 'Arrays.walk does crash on invalid path')

    def test_i18n(self):
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        trans = t('%s', ['Hello world'])
        self.assertEqual(trans, 'Hello world', 'Basic %s translation does not work')

    def test_dict_index(self):
        dic = {"foo": "bar", "tes": "test"}
        key = Arrays.dict_index(dic, 'test')
        self.assertEqual(key, 'tes', "Arrays.dict_index() failed.")

    def test_dict_map(self):
        dic = {"foo": "bar", "tes": {"test": "two"}}
        Arrays.map_dict_values_only(lambda s: s + "3", dic)
        self.assertEqual(dic['foo'], 'bar3', 'Arrays.map_dict#1 failed.')
        self.assertEqual(dic['tes']['test'], 'two3', 'Arrays.map_dict#1 failed.')


if __name__ == '__main__':
    unittest.main()
