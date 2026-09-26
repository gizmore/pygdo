import unittest
from gdotest.TestUtil import GDOTestCase
from unittest.mock import Mock, patch

from gdo.base.Method import Method
from gdo.base.WithPermissionCheck import WithPermissionCheck


class MethodPriceTest(GDOTestCase):
    def setUp(self):
        self.method = object.__new__(Method)
        self.user = Mock()
        self.method.err = Mock()

    def test_free_default_does_not_require_payment(self):
        self.assertEqual(0.0, self.method.gdo_method_price())
        with patch('gdo.base.WithPermissionCheck.module_enabled') as enabled:
            self.assertTrue(self.method.has_price_permission(self.user))
            enabled.assert_not_called()

    def test_balance_checked_even_after_cached_permission(self):
        self.method.gdo_method_price = lambda: 2.5
        WithPermissionCheck.CACHE[Method] = {self.user: True}
        self.addCleanup(WithPermissionCheck.CACHE.pop, Method, None)
        setting = Mock()
        with patch('gdo.base.WithPermissionCheck.module_enabled', return_value=True), \
                patch('gdo.core.GDO_UserSetting.GDO_UserSetting.get_setting', return_value=setting):
            setting.gdo_val.return_value = '3'
            self.assertTrue(self.method.has_permission(self.user))
            setting.gdo_val.return_value = '2'
            self.assertFalse(self.method.has_permission(self.user, False))
            self.method.err.assert_not_called()
            self.assertFalse(self.method.has_permission(self.user))
            self.method.err.assert_called_with('err_method_credits', ('2.5', '2'))

    def test_missing_module_denies_paid_method(self):
        self.method.gdo_method_price = lambda: 1.0
        with patch('gdo.base.WithPermissionCheck.module_enabled', return_value=False):
            self.assertFalse(self.method.has_price_permission(self.user))

    def test_missing_setting_denies_paid_method(self):
        self.method.gdo_method_price = lambda: 1.0
        with patch('gdo.base.WithPermissionCheck.module_enabled', return_value=True), \
                patch('gdo.core.GDO_UserSetting.GDO_UserSetting.get_setting', return_value=None):
            self.assertFalse(self.method.has_price_permission(self.user))
