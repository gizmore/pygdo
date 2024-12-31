from typing import TYPE_CHECKING

from gdo.base.Application import Application

if TYPE_CHECKING:
    from gdo.base.GDO import GDO

import mysql.connector
from mysql.connector import ProgrammingError, DatabaseError, IntegrityError
from mysql.connector.conversion import MySQLConverter

from gdo.base.Exceptions import GDODBException
from gdo.base.Logger import Logger
from gdo.base.Result import Result


class NopeConverter(MySQLConverter):
    def row_to_python(self, row_data: tuple[bytearray], desc: list):
        return map(lambda val: val.decode('utf-8') if val is not None else val, row_data)

    # def row_to_python(self, row_data, desc):
    #     return [self._decode_binary(val) if desc[i][1] == FieldType.BLOB else val for i, val in enumerate(row_data)]
    #
    # def _decode_binary(self, value):
    #     if isinstance(value, bytearray):
    #         # If it's binary data, handle it appropriately
    #         # For example, you might want to decode it using a specific encoding
    #         return value.decode('utf-8')
    #     else:
    #         # If it's not binary data, return it as is
    #         return value


class Database:
    db_host: str
    db_name: str
    username: str
    password: str
    locks: list[str]

    def __init__(self, host, name, user, pw):
        self.link = None
        self.db_host = host
        self.db_name = name
        self.username = user
        self.password = pw
        self.locks = []

    def __del__(self):
        if self.link:
            self.link.close()
            delattr(self, 'link')

    def get_link(self):
        if self.link is None:
            self.link = mysql.connector.connect(
                host=self.db_host,
                user=self.username,
                password=self.password,
                converter_class=NopeConverter,
            )
            self.link.autocommit = True
            self.link.database = self.db_name
            self.query('SET NAMES utf8mb4')
            self.query("SET time_zone = '+00:00'")
        return self.link

    def insert_id(self) -> str:
        return self.get_link().insert_id()

    def query(self, query):
        from gdo.base.Application import Application
        if Application.config('db.debug') != '0':
            Logger.debug("#" + str(Application.DB_READS + Application.DB_WRITES + 1) + ": " + query)
        try:
            Application.DB_WRITES += 1
            return self.get_link().cmd_query(query)
        except (ProgrammingError, DatabaseError, IntegrityError) as ex:
            raise GDODBException(ex.msg, query)

    def select(self, query: str, dictionary: bool = True):
        from gdo.base.Application import Application
        try:
            Application.DB_READS += 1
            cursor = self.cursor(dictionary)
            cursor.execute(query)
            return Result(cursor)
        except (ProgrammingError, DatabaseError, IntegrityError) as ex:
            raise GDODBException(ex.msg, query)

    def cursor(self, dictionary=True):
        return self.get_link().cursor(dictionary=dictionary, buffered=True)

    def create_table(self, gdo: 'GDO'):
        cols = []
        prim = []
        # uniq = []
        for gdt in gdo.columns():
            if define := gdt.gdo_column_define():
                cols.append(define)
                if gdt.is_primary():
                    prim.append(gdt.get_name())
                # if gdt.is_unique():
                #     uniq.append(gdt.get_name())
        if prim:
            primary = ",".join(prim)
            cols.append(f"PRIMARY KEY ({primary})")
        # for unique in uniq:
        #     cols.append(f"CONSTRAINT {gdo.gdo_table_name()}_UNIQUE UNIQUE ({unique})")
        engine = 'MyISAM' if gdo.gdo_engine_fast() else 'InnoDB'
        query = f"CREATE TABLE IF NOT EXISTS {gdo.gdo_table_name()} (" + ",\n".join(cols) + f") ENGINE = {engine}"
        self.query(query)

    def create_table_fk(self, gdo: 'GDO'):
        from gdo.core.GDT_Unique import GDT_Unique
        self.delete_all_fk(gdo)
        for gdt in gdo.columns():
            if isinstance(gdt, GDT_Unique):
                cn = f"GDO__UNIQUE__{gdo.gdo_table_name()}__{gdt.get_name()}"
                self.query(f"ALTER TABLE {gdo.gdo_table_name()} ADD CONSTRAINT {cn} UNIQUE({', '.join(gdt._column_names)})")
            if fk := gdt.column_define_fk():
                cn = f"GDO__FK__{gdo.gdo_table_name()}__{gdt.get_name()}"
                self.query(f"ALTER TABLE {gdo.gdo_table_name()} ADD CONSTRAINT {cn} {fk}")
            if gdt.is_unique():
                cn = f"GDO__UNIQUE__{gdo.gdo_table_name()}__{gdt.get_name()}"
                self.query(f"ALTER TABLE {gdo.gdo_table_name()} ADD CONSTRAINT {cn} UNIQUE({gdt.get_name()})")


    def delete_all_fk(self, gdo: 'GDO'):
        from gdo.base.Application import Application
        try:
            self.foreign_keys(False)
            db_name = Application.config('db.name')
            query = (f'SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS '
                     f'WHERE CONSTRAINT_TYPE IN ("FOREIGN KEY", "UNIQUE") AND TABLE_SCHEMA = "{db_name}" AND TABLE_NAME="{gdo.gdo_table_name()}"')
            result = self.select(query, False)
            while cn := result.fetch_val():
                self.delete_fk(gdo, cn)
        finally:
            self.foreign_keys(True)

    def delete_fk(self, gdo: 'GDO', constraint_name: str):
        from gdo.base.Application import Application
        db_name = Application.config('db.name')
        if "UNIQUE" in constraint_name:
            query = f"ALTER TABLE {gdo.gdo_table_name()} DROP INDEX {constraint_name}"
        else:
            query = f"ALTER TABLE {gdo.gdo_table_name()} DROP FOREIGN KEY {constraint_name}"
        result = self.query(query)

    def is_configured(self):
        return self.db_host is not None

    def drop_table(self, tablename):
        # Logger.debug(f"Dropping table {tablename}")
        query = f"DROP TABLE IF EXISTS {tablename}"
        self.query(query)

    def foreign_keys(self, state: bool = False):
        query = f"SET FOREIGN_KEY_CHECKS = %i" % state
        return self.query(query)

    def lock(self, name: str):
        return self.query(f"GET LOCK '{name}'")

    def unlock(self, name: str):
        return self.query(f"RELEASE LOCK '{name}'")

    def affected_rows(self) -> int:
        return self.get_link().num_rows

    ###############
    # Transaction #
    ###############

    def begin(self):
        Application.DB_TRANSACTIONS += 0.5
        self.get_link().start_transaction()
        return self

    def is_in_transaction(self) -> bool:
        return self.get_link().in_transaction

    def commit(self):
        Application.DB_TRANSACTIONS += 0.5
        self.get_link().commit()
        return self

    def rollback(self):
        Application.DB_TRANSACTIONS += 0.25
        self.get_link().rollback()
        return self
