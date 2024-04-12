import os
import time
import toml

from gdo.base.Logger import Logger
from gdo.base.Util import Files


class Application:

    LANG_ISO = 'en'
    TIME = time.time()

    DB = None
    path: str
    config: dict

    @classmethod
    def init(cls, path):
        from gdo.base.Database import Database
        # Logger.debug("Setting timezone to UTC")
        os.environ['TZ'] = 'UTC'
        time.tzset()
        # Logger.debug("Loading config")
        cls.path = os.path.normpath(path)
        config_path = os.path.join(cls.path, 'protected/config.toml')
        if Files.exists(config_path):
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

    @classmethod
    def now(cls):
        pass

