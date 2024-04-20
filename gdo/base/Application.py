import os
import threading
import time
import toml

from gdo.base.Render import Mode
from gdo.base.Util import Arrays


class Application:
    STORAGE = threading.local()
    LANG_ISO = 'en'
    TIME = time.time()

    DB = None
    PATH: str
    CONFIG: dict[str, str] = {}

    @classmethod
    def tick(cls):
        cls.TIME = time.time()

    @classmethod
    def init(cls, path):
        from gdo.base.Database import Database
        os.environ['TZ'] = 'UTC'
        time.tzset()
        cls.STORAGE.mode = Mode.HTML
        cls.STORAGE.user = None
        cls.tick()
        cls.PATH = os.path.normpath(path) + '/'
        config_path = os.path.join(cls.PATH, 'protected/config.toml')
        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                cls.CONFIG = toml.load(f)
                cfg = cls.CONFIG['db']
                cls.DB = Database(cfg['host'], cfg['name'], cfg['user'], cfg['pass'])
        else:
            from gdo.install.Config import Config
            cls.CONFIG = Config.defaults()
        cls.get_page().init()

    @classmethod
    def reset(cls):
        cls.get_page().init()

    @classmethod
    def has_db(cls):
        return cls.DB is not None

    @classmethod
    def file_path(cls, path: str):
        return os.path.join(cls.PATH, path)

    @classmethod
    def set_current_user(cls, user):
        cls.STORAGE.user = user

    @classmethod
    def get_page(cls):
        from gdo.ui.GDT_Page import GDT_Page
        if not hasattr(cls.STORAGE, 'page'):
            cls.STORAGE.page = GDT_Page()
        return cls.STORAGE.page

    @classmethod
    def mode(cls, mode: Mode):
        cls.STORAGE.mode = mode

    @classmethod
    def get_mode(cls) -> Mode:
        return cls.STORAGE.mode

    @classmethod
    def is_html(cls) -> bool:
        return cls.get_mode().value < 10

    @classmethod
    def config(cls, path: str, default: str = '') -> str:
        return Arrays.walk(cls.CONFIG, path) or default

    @classmethod
    def storage(cls, key: str, default: str = '') -> str:
        return cls.STORAGE.__getattribute__(key) or default

    @classmethod
    def init_web(cls, request):
        cls.STORAGE.ip = request.get_remote_host()
        pass

    @classmethod
    def init_cli(cls):
        cls.STORAGE.ip = '::1'
        pass
