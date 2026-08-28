import tomlkit

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO import GDO
from gdo.base.GDO_GDOTable import GDO_GDOTable
from gdo.base.GDO_Module import GDO_Module
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Render
from gdo.base.Result import ResultType
from gdo.base.Util import Arrays, msg, Files, gdo_print
from gdo.core.GDO_User import GDO_User


class Installer:

    @classmethod
    async def install_modules(cls, modules: list[GDO_Module], verbose: bool = False):
        if verbose:
            gdo_print("Collecting modules and dependencies.")
        modules = cls.modules_with_deps(modules)

        if verbose:
            gdo_print(f"Installing {len(modules)} module entries.")
        for module in modules:
            await cls.install_module(module, verbose)

        if verbose:
            gdo_print("Re-Loading installed modules.")
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        # ``load_modules_db`` imports the freshly installed module, but the
        # running process also needs its methods registered immediately.  In
        # particular, ``safe.install`` must not require a Dog restart before
        # the new module's text commands can be used.
        loader.init_cli()
        cls.migrate_user_settings()

        if verbose:
            gdo_print("Calling module install hooks")
        for module in modules:
            await module.gdo_install()
        return True

    @classmethod
    def migrate_user_settings(cls):
        """Synchronise the settings-key enum after all modules registered it.

        User settings are contributed by many modules but share the one
        ``gdo_usersetting.uset_key`` enum column owned by core.  Creating an
        already existing table cannot extend that enum, so a later module
        install otherwise leaves its new settings impossible to persist.
        """
        from gdo.core.GDO_UserSetting import GDO_UserSetting

        table = GDO_UserSetting.table()
        key = table.column('uset_key')
        # The table can have been created before enabled modules registered
        # their settings.  GDT_Select caches its initial choices, so rebuild
        # this enum from the now complete GDT_UserSetting.KNOWN registry.
        if hasattr(key, '_choices'):
            del key._choices
        Application.db().query(
            f"ALTER TABLE {table.gdo_table_name()} MODIFY COLUMN {key.gdo_column_define()}"
        )

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
    async def install_module(cls, module: GDO_Module, verbose: bool = False) -> bool:
        try:
            if not module.is_installable():
                return False
            if verbose:
                print(f"Installing module {Render.bold(module.get_name)}")
            classes = module.gdo_classes()
            for classname in classes:
                if verbose:
                    print(f"[+] Installing table {classname.__name__.lower()}")
                cls.install_gdo(classname)
            for classname in classes:
                cls.install_gdo_fk(classname)
            module = cls.install_module_entry(module)
            ModuleLoader.instance().on_module_installed(module)
            for classname in classes:
                cls.install_gdo_table(classname)
            return True
        except Exception as ex:
            Logger.exception(ex)
            return False

    @classmethod
    def install_module_entry(cls, module: GDO_Module):
        loader = ModuleLoader.instance()
        db = loader.load_module_db(module.get_name)
        if db is not None:
            # vals() clears dirty state.  Reinstalling a previously disabled
            # module must therefore explicitly persist its enabled flag.
            module = db
            module.save_vals({
                'module_enabled': '1',
                'module_priority': str(module._priority),
            })
        else:
            module.vals({
                'module_id': '0',
                'module_name': module.get_name,
                'module_enabled': '1',
                'module_priority': str(module._priority),
                'module_sort': str(module._priority),
            })
            module.all_dirty().soft_replace()

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
                db.foreign_keys(False)
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
        cls.migrate_user_settings()

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
            module.set_val('module_enabled', '0')
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
        return cls.load_provider_toml()[module.get_name]

    @classmethod
    def wipe_all(cls, database: str = None):
        database = Application.config('db.name') if database is None else database
        Application.db().query(f"DROP DATABASE {database}")
        Application.db().query(f"CREATE DATABASE {database}")
        Application.db().query(f"USE {database}")
