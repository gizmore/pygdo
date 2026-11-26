import subprocess
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from gdoadm import App
from gdo.install.Installer import Installer


class MigrateProvisionTest(unittest.IsolatedAsyncioTestCase):
    async def test_provides_then_installs_then_migrates(self):
        loader = MagicMock()
        module = object()
        loader.load_modules_fs.return_value = {'mira': module}
        events = []
        with patch('sys.argv', ['gdoadm.py', 'migrate', 'mira']), \
                patch('gdoadm.ModuleLoader.instance', return_value=loader), \
                patch('gdoadm.subprocess.run', side_effect=lambda cmd, **kw: events.append(cmd)), \
                patch('gdoadm.Installer.migrate_modules', side_effect=lambda modules: events.append(modules)):
            await App().migrate()
        self.assertEqual([
            ['./gdo_adm.sh', 'provide', '--yes', '--no-install', 'mira'],
            ['./gdo_adm.sh', 'install', '--reinstall', '--strict', 'mira'],
            [module],
        ], events)

    async def test_failed_provide_stops_install_and_migration(self):
        with patch('sys.argv', ['gdoadm.py', 'migrate', 'mira']), \
                patch('gdoadm.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'provide')) as run, \
                patch('gdoadm.Installer.migrate_modules') as migrate:
            with self.assertRaises(subprocess.CalledProcessError):
                await App().migrate()
        self.assertEqual(1, run.call_count)
        migrate.assert_not_called()

    async def test_strict_install_failure_stops_before_migration(self):
        with patch('sys.argv', ['gdoadm.py', 'migrate', 'mira']), \
                patch('gdoadm.subprocess.run', side_effect=[None, subprocess.CalledProcessError(1, 'install')]), \
                patch('gdoadm.Installer.migrate_modules') as migrate:
            with self.assertRaises(subprocess.CalledProcessError):
                await App().migrate()
        migrate.assert_not_called()

    async def test_strict_install_reports_module_failure(self):
        module = MagicMock()
        module.is_installable.return_value = True
        module.get_name = 'mira'
        with patch.object(Installer, 'modules_with_deps', return_value=[module]), \
                patch.object(Installer, 'install_module', new_callable=AsyncMock, return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'Installation failed for module mira'):
                await Installer.install_modules([module], strict=True)

    async def test_all_operates_on_installed_modules_not_all_providers(self):
        loader = MagicMock()
        modules = {'mira': object(), 'chat': object()}
        loader.load_modules_fs.return_value = modules
        with patch('sys.argv', ['gdoadm.py', 'migrate', '--all']), \
                patch('gdoadm.ModuleLoader.instance', return_value=loader), \
                patch('gdoadm.subprocess.run') as run, \
                patch('gdoadm.Installer.migrate_modules') as migrate:
            await App().migrate()
        self.assertEqual(['./gdo_adm.sh', 'provide', '--yes', '--no-install', 'mira,chat'], run.call_args_list[0].args[0])
        self.assertEqual(['./gdo_adm.sh', 'install', '--reinstall', '--strict', 'mira,chat'], run.call_args_list[1].args[0])
        migrate.assert_called_once_with(list(modules.values()))

    async def test_provide_no_install_does_not_install_existing_module(self):
        loader = MagicMock()
        loader.load_modules_fs.return_value = {'mira': object()}
        providers = {'mira': (['https://example.test/mira.git'], [], False)}
        with patch('sys.argv', ['gdoadm.py', 'provide', '--yes', '--no-install', 'mira']), \
                patch('gdoadm.ModuleLoader.instance', return_value=loader), \
                patch.object(App, '_load_provider_toml', return_value=providers), \
                patch('gdoadm.subprocess.run') as run:
            await App().provide()
        run.assert_not_called()

    async def test_provide_checks_dependencies_of_existing_module(self):
        loader = MagicMock()
        loader.load_modules_fs.return_value = {'mira': object()}
        providers = {
            'mira': (['https://example.test/mira.git'], ['dependency'], False),
            'dependency': (['https://example.test/dependency.git'], [], False),
        }
        with patch('sys.argv', ['gdoadm.py', 'provide', '--yes', '--no-install', 'mira']), \
                patch('gdoadm.ModuleLoader.instance', return_value=loader), \
                patch.object(App, '_load_provider_toml', return_value=providers), \
                patch.object(App, 'post_install'), \
                patch('gdoadm.Application.file_path', side_effect=lambda path='': '/tmp/' + path), \
                patch('gdoadm.os.chdir'), \
                patch('gdoadm.subprocess.run') as run:
            await App().provide()
        run.assert_called_once_with(['git', 'clone', 'https://example.test/dependency', '/tmp/gdo/dependency'], check=True)


class MigrateErrorTest(unittest.TestCase):
    def test_failed_temp_creation_is_reported_without_dropping_an_existing_temp_table(self):
        db = MagicMock()
        db.query.side_effect = RuntimeError('create failed')
        table = MagicMock()
        table.gdo_table_name.return_value = 'gdo_test'
        with patch('gdo.install.Installer.Application.db', return_value=db), \
                patch('gdo.install.Installer.Logger.exception'):
            with self.assertRaisesRegex(RuntimeError, 'create failed'):
                Installer.migrate_gdo(table)
        db.drop_table.assert_not_called()
        db.foreign_keys.assert_any_call(True)

    def test_failed_rebuild_restores_snapshot_and_propagates_failure(self):
        db = MagicMock()
        db.create_table.side_effect = RuntimeError('rebuild failed')
        table = MagicMock()
        table.gdo_table_name.return_value = 'gdo_test'
        with patch('gdo.install.Installer.Application.db', return_value=db), \
                patch('gdo.install.Installer.Logger.exception'), \
                patch.object(Installer, 'column_names', return_value=['id']):
            with self.assertRaisesRegex(RuntimeError, 'rebuild failed'):
                Installer.migrate_gdo(table)
        db.query.assert_any_call('RENAME TABLE zzz_temp_gdo_test TO gdo_test')
        self.assertNotIn(unittest.mock.call('zzz_temp_gdo_test'), db.drop_table.call_args_list)
