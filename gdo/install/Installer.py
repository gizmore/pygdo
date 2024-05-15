from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDO import GDO
from gdo.base.GDO_Module import GDO_Module
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Result import ResultType
from gdo.base.Util import Arrays, msg


class Installer:

    @classmethod
    def install_modules(cls, modules: list[GDO_Module], verbose: bool = False):
        first = True
        for module in cls.modules_with_deps(modules):
            cls.install_module(module, verbose, first)
            if module.get_name() != 'base':
                first = False

    @classmethod
    def modules_with_deps(cls, modules: list) -> [GDO_Module]:
        loader = ModuleLoader.instance()
        modules.append(loader.load_module_fs('core'))
        deps = Arrays.unique(modules)
        before = len(deps)
        after = 0

        # out = []
        # for module in modules:
        #     out.append(module.get_name)
        # print(", ".join(out))

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
    def install_module(cls, module: GDO_Module, verbose: bool = False, install_settings: bool = False) -> bool:
        if verbose:
            print(f"Installing module {module.get_name()}")
        if not module.is_installable():
            return False
        classes = module.gdo_classes()
        for classname in classes:
            if verbose:
                print(f"Installing table {str(classname.__name__).lower()}")
            cls.install_gdo(classname)
        cls.install_module_entry(module)
        ModuleLoader.instance().init_user_settings()
        module.init()
        if module.get_name() != 'base' and install_settings:
            from gdo.core import module_core
            if verbose:
                print("Migrating core for user settings...")
            Installer.migrate_module(module_core.instance())
        module.gdo_install()
        return True

    @classmethod
    def install_module_entry(cls, module: GDO_Module):
        loader = ModuleLoader.instance()
        db = loader.load_module_db(module.get_name())
        mid = '0'
        if db is not None:
            mid = db.get_id()
        module._vals.update({
            'module_id': mid,
            'module_name': module.get_name(),
            'module_enabled': '1',
            'module_priority': str(module._priority),
        })
        module.all_dirty(db is None)
        module.soft_replace()

    @classmethod
    def install_gdo(cls, classname):
        table = Cache.table_for(classname)
        return Application.db().create_table(table)

    @classmethod
    def migrate_module(cls, module: GDO_Module):
        for classname in module.gdo_classes():
            table = Cache.table_for(classname)
            cls.migrate_gdo(table)
        pass

    @classmethod
    def migrate_gdo(cls, gdo: GDO):
        db = Application.db()
        try:
            db.foreign_keys(False)
            # Remove old temp table
            tablename = gdo.gdo_table_name()
            temptable = f"zzz_temp_{tablename}"
            # create temp and copy as old
            db.drop_table(temptable)
            query = f"SHOW CREATE TABLE {tablename}"
            result = db.select(query, False)
            query = result.fetch_row()[1]
            query = query.replace(tablename, temptable)
            db.query(query)
            query = f"INSERT INTO {temptable} SELECT * FROM {tablename}"
            db.query(query)

            query = f"DROP TABLE {tablename}"
            db.query(query)
            db.create_table(gdo)

            # calculate columns and copy back in new
            cols = cls.column_names(gdo, temptable)

            columns = ",".join(cols)

            query = f"INSERT INTO {tablename} ({columns}) SELECT {columns} FROM {temptable}"
            db.query(query)

            # drop temp after all succeded.
            query = f"DROP TABLE {temptable}"
            db.query(query)
        except Exception as ex:
            Logger.exception(ex)
        finally:
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
        if old and new:
            return list(set(old).intersection(new))
        return []

    @classmethod
    def wipe(cls, module: GDO_Module):
        for klass in reversed(module.gdo_classes()):
            Application.db().drop_table(klass.table().gdo_table_name())
        module.delete()
