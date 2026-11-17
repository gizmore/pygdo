import unittest
from importlib import import_module
from importlib.util import find_spec
from unittest.mock import MagicMock

from gdo.account.method.linked import linked
from gdo.base.WithPermissionCheck import WithPermissionCheck
from gdo.core.method.servers import servers
from gdo.file.method.files import files
from gdo.file.method.seo_files import seo_files
from gdo.form.MethodForm import MethodForm
from gdo.table.MethodQueryTable import MethodQueryTable
from gdo.table.MethodTable import MethodTable


class TableAuthenticationTest(unittest.TestCase):
    def test_table_defaults_public_but_forms_remain_private(self):
        self.assertFalse(MethodTable.gdo_needs_authentication(None))
        self.assertFalse(MethodQueryTable.gdo_needs_authentication(None))
        self.assertTrue(MethodForm.gdo_needs_authentication(None))

    def test_sensitive_tables_keep_authentication(self):
        methods = [files, seo_files, linked, servers]
        for module, cls in (('gdo.git.method.git_repos', 'git_repos'),
                            ('gdo.oracle.method.answers', 'answers'),
                            ('gdo.payment.method.orders', 'orders'),
                            ('gdo.pm.method.folder', 'folder'),
                            ('gdo.pm.method.folders', 'folders')):
            if find_spec('.'.join(module.split('.')[:2])) is not None:
                methods.append(getattr(import_module(module), cls))
        for method in methods:
            with self.subTest(method=method.__name__):
                self.assertTrue(method.gdo_needs_authentication(None))

    def test_explicit_permission_still_rejects_guests(self):
        method = MagicMock()
        method.gdo_user_permission.return_value = 'staff'
        method.gdo_needs_authentication.return_value = False
        user = MagicMock()
        user.is_system.return_value = False
        user.is_authenticated.return_value = False
        self.assertFalse(WithPermissionCheck.has_permission(method, user, display_error=False))
