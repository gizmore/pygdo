import tomlkit

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO import GDO
from gdo.base.GDO_GDOTable import GDO_GDOTable
from gdo.base.GDO_Module import GDO_Module
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Result import ResultType
from gdo.base.Util import Arrays, msg, Files
from gdo.core.GDO_UserSetting import GDO_UserSetting
from gdo.core.method.clear_cache import clear_cache


class Installer:

    @classmethod
    def install_modules(cls, modules: list[GDO_Module], verbose: bool = False):
        if verbose:
            print("Collecting modules and dependencies.")
        modules = cls.modules_with_deps(modules)

        if verbose:
            print(f"Installing {len(modules)} module entries.")
        for module in modules:
            cls.install_module(module, verbose)

        if verbose:
            print("Re-Loading installed modules.")
        loader = ModuleLoader.instance()
        Cache.clear()
        loader.reset()
        modules = loader.load_modules_db()
        loader.init_modules(True, True)

        if verbose:
            print("Migrating core for user settings.")
        Installer.migrate_gdo(GDO_UserSetting.table())

        if verbose:
            print("Calling module install hooks")
        for module in modules:
            try:
                module.gdo_install()
            except Exception as ex:
                Logger.exception(ex)
                return False
        clear_cache().gdo_execute()
        return True

    @classmethod
    def modules_with_deps(cls, modules: list) -> [GDO_Module]:
        loader = ModuleLoader.instance()
        modules.append(loader.load_module_fs('core'))
        deps = Arrays.unique(modules)
        before = len(deps)
        after = 0

        while before != after:
            before = after
            for dep in deps:
                more = dep.gdo_dependencies()
                for name in more:
                    mod = loader.load_module_fs(name)
                    if mod not in deps:
                        deps.append(mod)
            after = len(deps)
        return sorted(deps, key=lambda m: m._priority)

    @classmethod
    def install_module(cls, module: GDO_Module, verbose: bool = False) -> bool:
        if verbose:
            print(f"Installing module {module.get_name()}")
        if not module.is_installable():
            return False
        classes = module.gdo_classes()
        for classname in classes:
            if verbose:
                print(f"Installing table {str(classname.__name__).lower()}")
            cls.install_gdo(classname)
        for classname in classes:
            cls.install_gdo_fk(classname)
        module = cls.install_module_entry(module)
        ModuleLoader.instance().on_module_installed(module)
        for classname in classes:
            cls.install_gdo_table(classname)
        return True

    @classmethod
    def install_module_entry(cls, module: GDO_Module):
        loader = ModuleLoader.instance()
        db = loader.load_module_db(module.get_name())
        mid = '0'
        if db is not None:
            mid = db.get_id()
            module = db
        module.vals({
            'module_id': mid,
            'module_name': module.get_name(),
            'module_enabled': '1',
            'module_priority': str(module._priority),
        })
        module.all_dirty(db is None)
        module.soft_replace()

        return module

    @classmethod
    def install_gdo(cls, class_name):
        table = Cache.table_for(class_name)
        return Application.db().create_table(table)

    @classmethod
    def install_gdo_table(cls, class_name: str):
        GDO_GDOTable.register_table(class_name)

    @classmethod
    def install_gdo_fk(cls, class_name: str):
        table = Cache.table_for(class_name)
        return Application.db().create_table_fk(table)

    @classmethod
    def migrate_module(cls, module: GDO_Module):
        for class_name in module.gdo_classes():
            table = Cache.table_for(class_name)
            cls.migrate_gdo(table)

    @classmethod
    def migrate_gdo(cls, gdo: GDO):
        db = Application.db()
        restore_from_zzz = False # If error occurs, try to rename zzz table to table
        tablename = gdo.gdo_table_name()
        temptable = f"zzz_temp_{tablename}"
        try:
            db.foreign_keys(False)
            result = db.select(f"SHOW CREATE TABLE {tablename}", False)
            query = result.fetch_row()[1]
            query = query.replace(tablename, temptable)
            db.query(query)  # CREATE TABLE zzz% like old
            if cols := cls.column_names(gdo, temptable):  # something changed?
                columns = ",".join(cols)
                db.query(f"INSERT INTO {temptable} SELECT * FROM {tablename}")  # copy old to zzz
                restore_from_zzz = True  # At this point we can restore on error
                db.drop_table(tablename)  # Drop old
                db.create_table(gdo)  # Create new
                db.create_table_fk(gdo)  # with FKs
                db.query(f"INSERT INTO {tablename} ({columns}) SELECT {columns} FROM {temptable}")  # Copy zzz to new
        except Exception as ex:
            Logger.exception(ex)
            if restore_from_zzz:
                db.drop_table(tablename)  # Remove old temp table
                db.query(f"RENAME TABLE {temptable} TO {tablename}")
                db.create_table_fk(gdo)
        finally:
            db.drop_table(temptable)  # Remove old temp table
            db.foreign_keys(True)

    @classmethod
    def migrate_modules(cls, modules):
        for module in modules:
            cls.migrate_module(module)

    @classmethod
    def column_names(cls, gdo, temptable) -> list:

        db = Application.db()

        # Old column names
        query = ('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS '
                 f"WHERE TABLE_SCHEMA = '{db.db_name}' AND TABLE_NAME = '{temptable}'"
                 )
        result = db.select(query, False)
        rows = result.iter(ResultType.ROW).fetch_all()
        old = map(lambda c: c[0], rows)

        # New column names
        query = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                 f"WHERE TABLE_SCHEMA = '{db.db_name}' AND TABLE_NAME = '{gdo.gdo_table_name()}'")
        result = db.select(query, False)
        rows = result.iter(ResultType.ROW).fetch_all()
        new = map(lambda c: c[0], rows)
        if old == new:
            return []
        if old and new:
            return list(set(old).intersection(new))
        return []

    @classmethod
    def wipe(cls, module: GDO_Module):
        db = Application.db()
        try:
            db.foreign_keys(False)
            for klass in reversed(module.gdo_classes()):
                db.drop_table(klass.table().gdo_table_name())
            db.foreign_keys(True)
            module.delete()
        except Exception as ex:
            Logger.exception(ex)
        finally:
            db.foreign_keys(True)

    @classmethod
    def load_provider_toml(cls):
        path = Application.file_path('gdo/base/res/deps.toml')
        content = Files.get_contents(path)
        return tomlkit.loads(content)

    @classmethod
    def get_repo_info(cls, module: GDO_Module):
        return cls.load_provider_toml()[module.get_name()]
