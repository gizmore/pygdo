import mysql.connector
from mysql.connector import ProgrammingError

from gdo.base.Exceptions import GDODBException
from gdo.base.Logger import Logger
from gdo.base.Result import Result


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
            )
            self.link.autocommit = True
            self.link.database = self.db_name
            self.query('SET NAMES utf8mb4')
        return self.link

    def insert_id(self) -> str:
        return self.get_link().insert_id()

    def query(self, query):
        try:
            return self.get_link().cmd_query(query)
        except ProgrammingError as ex:
            raise GDODBException(ex.msg, query)

    def select(self, query: str):
        cursor = self.cursor()
        cursor.execute(query)
        return Result(cursor)

    def cursor(self, dictionary=True):
        return self.get_link().cursor(False, False, dictionary=dictionary)

    def create_table(self, gdo):
        cols = []
        prim = []
        for gdt in gdo.columns():
            define = gdt.gdo_column_define()
            cols.append(define)
            if gdt.is_primary():
                prim.append(gdt.get_name())
        if prim:
            primary = ",".join(prim)
            cols.append(f"PRIMARY KEY ({primary})")
        query = f"CREATE TABLE IF NOT EXISTS {gdo.gdo_table_name()} (" + ",\n".join(cols) + ")\n"
        self.query(query)

    def is_configured(self):
        return self.db_host is not None

    def drop_table(self, tablename):
        # Logger.debug(f"Dropping table {tablename}")
        query = f"DROP TABLE IF EXISTS {tablename}"
        self.query(query)

    def foreign_keys(self, state=False):
        query = f"SET FOREIGN_KEY_CHECKS = %i" % state
        return self.query(query)

    def lock(self, name: str):
        return self.query(f"GET LOCK '{name}'")

    def unlock(self, name: str):
        return self.query(f"RELEASE LOCK '{name}'")
