import os
import time
import toml


class Application:
    LANG_ISO = 'en'
    TIME = time.time()

    DB = None
    PATH: str
    CONFIG: dict[str, any]

    @classmethod
    def tick(cls):
        cls.TIME = time.time()

    @classmethod
    def init(cls, path):
        from gdo.base.Database import Database
        os.environ['TZ'] = 'UTC'
        time.tzset()
        cls.tick()
        cls.PATH = os.path.normpath(path) + '/'
        config_path = os.path.join(cls.PATH, 'protected/config.toml')
        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                cls.CONFIG = toml.load(f)
                cfg = cls.CONFIG['db']
                cls.DB = Database(cfg['host'], cfg['name'], cfg['user'], cfg['pass'])

    @classmethod
    def has_db(cls):
        return cls.DB is not None

    @classmethod
    def file_path(cls, path: str):
        return os.path.join(cls.PATH, path)

    # @classmethod
    # def now(cls):
    #     pass
