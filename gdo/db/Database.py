import mysql.connector
from mysql.connector import ProgrammingError

from gdo.core.Exceptions import GDODBException
from gdo.core.Logger import Logger


class Database:
    db_host: str
    db_name: str
    username: str
    password: str

    def __init__(self, host, name, user, pw):
        self.link = None
        self.db_host = host
        self.db_name = name
        self.username = user
        self.password = pw

    def get_link(self):
        if self.link is None:
            self.link = mysql.connector.connect(
                host=self.db_host,
                user=self.username,
                password=self.password,
            )
            try:
                self.link.database = self.db_name
            except:
                pass
            self.query('SET NAMES utf8mb4')
        return self.link

    def query(self, query):
        try:
            return self.get_link().cmd_query(query)
        except ProgrammingError:
            print(query)
            raise GDODBException("Database error")

    def create_table(self, gdo):
        Logger.debug(f"Installing {gdo.gdo_table_name()}")
        cols = []
        prim = []
        for gdt in gdo.gdo_columns():
            Logger.debug(f"Field {gdt.get_name()}")
            define = gdt.gdo_column_define()
            cols.append(define)
            if gdt.is_primary():
                prim.append(gdt.get_name())

        query = f"CREATE TABLE IF NOT EXISTS {gdo.gdo_table_name()} (" + ",\n".join(cols) + ")\n"
        self.query(query)

    def is_configured(self):
        return self.db_host is not None

    def drop_table(self, tablename):
        Logger.debug(f"Dropping table {tablename}")
        query = f"DROP TABLE IF EXISTS {tablename}"
        self.query(query)

    def foreign_keys(self, state=False):
        query = f"SET FOREIGN_KEY_CHECKS = %i" % state
        return self.query(query)

    def fetch_rows(self, result):
        return self.get_link().get_rows()

    def fetch_row(self):
        return self.get_link().get_row()
