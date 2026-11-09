import unittest
from unittest.mock import MagicMock

from gdo.base.WithPermissionCheck import WithPermissionCheck


class PermissionAuthBoundaryTest(unittest.TestCase):
    def setUp(self):
        WithPermissionCheck.CACHE.clear()
        self.method = MagicMock()
        self.method.gdo_user_permission.return_value = 'owner'
        self.method.gdo_needs_authentication.return_value = False
        self.method.err_not_authenticated.return_value = False
        self.user = MagicMock()
        self.user.is_system.return_value = False
        self.user.is_authenticated.return_value = False

    def test_privileged_method_denies_before_cached_permission(self):
        WithPermissionCheck.CACHE[self.method.__class__] = {self.user: True}
        self.assertFalse(WithPermissionCheck.has_permission(self.method, self.user))
        self.method.err_not_authenticated.assert_called_once()

    def test_public_method_requiring_authentication_denies(self):
        self.method.gdo_user_permission.return_value = None
        self.method.gdo_needs_authentication.return_value = True
        self.assertFalse(WithPermissionCheck.has_permission(self.method, self.user, False))

    def test_authenticated_user_can_use_cached_permission(self):
        self.user.is_authenticated.return_value = True
        self.method.has_price_permission.return_value = True
        WithPermissionCheck.CACHE[self.method.__class__] = {self.user: True}
        self.assertTrue(WithPermissionCheck.has_permission(self.method, self.user))

    def test_internal_system_can_use_cached_permission(self):
        self.user.is_system.return_value = True
        self.method.has_price_permission.return_value = True
        WithPermissionCheck.CACHE[self.method.__class__] = {self.user: True}
        self.assertTrue(WithPermissionCheck.has_permission(self.method, self.user))
