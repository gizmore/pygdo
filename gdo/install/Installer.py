from gdo.core.Application import Application
from gdo.core.Cache import Cache
from gdo.core.GDO import GDO
from gdo.core.GDO_Module import GDO_Module
from gdo.core.Logger import Logger


class Installer:

    @classmethod
    def install_modules(cls, modules):
        for module in cls.modules_with_deps(modules):
            cls.install_module(module)

    @classmethod
    def modules_with_deps(cls, modules):
        depped = []
        return modules

    @classmethod
    def install_module(cls, module: GDO_Module):
        Logger.debug(f'Installing module {module.get_name()}')
        classes = module.gdo_classes()
        for classname in classes:
            Logger.debug(f'Installing module class {classname}')
            cls.install_gdo(classname)

    @classmethod
    def install_gdo(cls, classname):
        table = Cache.table_for(classname)
        cls.DB.create_table(table)
        pass

    @classmethod
    def migrate_module(cls, module: GDO_Module):
        for classname in module.gdo_classes():
            table = Cache.table_for(classname)
            cls.migrate_gdo(table)
        pass

    @classmethod
    def migrate_gdo(cls, gdo: GDO):
        db = Application.DB
        try:
            db.foreign_keys(False)
            # Remove old temp table
            tablename = gdo.gdo_table_name()
            temptable = "zzz_temp_{tablename}"
            # create temp and copy as old
            db.drop_table(temptable)
            query = f"SHOW CREATE TABLE {tablename}"
            result = db.query(query)
            query = result.fetch_row()
            query = query.replace(tablename, temptable)
            db.query(query)
            query = f"INSERT INTO {temptable} SELECT * FROM {tablename}"
            db.query(query)

            query = f"DROP TABLE {tablename}"
            db.query(query)
            db.create_table(gdo)

            # calculate columns and copy back in new
            colums = cls.column_names(gdo, temptable)

            columns = ",".join(colums)

            query = f"INSERT INTO {tablename} ({columns}) SELECT {columns} FROM {temptable}"
            db.query(query)

            # drop temp after all succeded.
            query = "DROP TABLE {temptable}"
            db.query(query)
        except:
            raise
        finally:
            db.foreign_keys(True)



    @classmethod
    def migrate_modules(cls, modules):
        for module in modules:
            cls.migrate_module(module)

    @classmethod
    def column_names(cls, gdo, temptable) -> list:

        db = Application.DB

        # Old column names
        query = ('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS '
            f"WHERE TABLE_SCHEMA = '{db.db_name}' AND TABLE_NAME = '{temptable}'"
        )
        result = db.query(query)
        rows = db.fetch_all_rows(result)
        old = rows.map(lambda c: c[0], rows)

        # New column names
        query = ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE TABLE_SCHEMA = '{db.db_name}' AND TABLE_NAME = '{gdo.gdo_table_name()}'")
        result = db.query(query)
        rows = db.fetch_all_rows(result)
        new = rows.map(lambda c: c[0], rows)
        if old and new:
            return list(set(old).intersection(new))
        return []







