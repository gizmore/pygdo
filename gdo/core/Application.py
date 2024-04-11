import os
import toml


class Application:
    DB = None
    path: str
    config: dict

    @classmethod
    def init(cls, path):
        from gdo.core.Database import Database
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
