import os
import toml
from gdo.db.Database import Database


class Application:

    path: str
    config: dict
    DB: Database

    @classmethod
    def init(cls, path):
        cls.count = 0
        cls.path = os.path.normpath(path)
        config_path = os.path.join(cls.path, 'protected/config.toml')
        with open(config_path, 'r') as f:
            cls.config = toml.load(f)
            cfg = cls.config['Database']['db']
            cls.DB = Database(cfg['host'], cfg['name'], cfg['user'], cfg['pass'])

    @classmethod
    def has_db(cls):
        return cls.DB is not None

    @classmethod
    def file_path(cls, path: str):
        return os.path.join(cls.path, path)

