import os
import sys
import threading
import time
import toml

from gdo.base.Events import Events
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Util import Arrays, dump


class Application:
    RUNNING = True
    PROTOCOL = 'http'
    LOADER: object
    EVENTS: 'Events'
    STORAGE = threading.local()
    LANG_ISO = 'en'
    TIME = time.time()

    DB: object
    PATH: str
    CONFIG: dict[str, str] = {}

    @classmethod
    def tick(cls):
        cls.TIME = time.time()
        cls.STORAGE.time_start = cls.TIME
        cls.EVENTS.update_timers(cls.TIME)

    @classmethod
    def init(cls, path):
        from gdo.base.Cache import Cache
        from gdo.base.Database import Database
        from gdo.base.ModuleLoader import ModuleLoader
        # Cache.init()
        cls.PATH = os.path.normpath(path) + '/'
        os.environ['TZ'] = 'UTC'
        time.tzset()
        cls.LOADER = ModuleLoader()
        cls.EVENTS = Events()
        Application.init_common()
        config_path = 'protected/config_test.toml' if 'unittest' in sys.modules.keys() else 'protected/config.toml'
        config_path = os.path.join(cls.PATH, config_path)
        cls.get_page().init()
        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                cls.CONFIG = toml.load(f)
                cfg = cls.CONFIG['db']
                cls.DB = Database(cfg['host'], cfg['name'], cfg['user'], cfg['pass'])
        else:
            from gdo.install.Config import Config
            cls.CONFIG = Config.defaults()

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
    def fresh_page(cls):
        from gdo.ui.GDT_Page import GDT_Page
        cls.STORAGE.page = GDT_Page()
        return cls.get_page()

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
    def storage(cls, key: str, default: any) -> str:
        if hasattr(cls.STORAGE, key):
            return cls.STORAGE.__getattribute__(key)
        elif default:
            cls.STORAGE.__setattr__(key, default)
        return default

    @classmethod
    def init_cli(cls):
        cls.STORAGE.ip = '::1'
        cls.STORAGE.cookies = {}
        cls.STORAGE.time_start = time.time()
        cls.mode(Mode.CLI)

    @classmethod
    def init_web(cls, environ):
        cls.STORAGE.time_start = float(environ.get('mod_wsgi.request_start')) / 1000000.0
        cls.STORAGE.environ = environ
        cls.STORAGE.headers = {}
        cls.init_cookies(environ)
        cls.STORAGE.ip = environ.get('REMOTE_ADDR')
        cls.PROTOCOL = environ['REQUEST_SCHEME']
        cls.mode(Mode.HTML)

    @classmethod
    def init_common(cls):
        cls.tick()
        Logger.init()
        cls.STORAGE.mode = Mode.HTML
        cls.STORAGE.user = None
        cls.STORAGE.db_reads = 0
        cls.STORAGE.db_writes = 0
        cls.STORAGE.db_queries = 0

    @classmethod
    def init_cookies(cls, environ):
        cookies = {}
        cookies_str = environ.get('HTTP_COOKIE', '')
        # if cookies_str:
        for cookie in cookies_str.split(';'):
            parts = cookie.strip().split('=', 1)
            if len(parts) == 2:
                name, value = cookie.split('=', 1)
                cookies[name] = value
        cls.STORAGE.cookies = cookies

    @classmethod
    def status(cls, status: str):
        cls.STORAGE.status = status

    @classmethod
    def get_status(cls):
        return cls.storage('status', "200 OK")

    @classmethod
    def header(cls, name: str, value: str):
        headers = cls.storage('headers', {})
        headers[name] = value
        cls.STORAGE.headers = headers

    @classmethod
    def get_headers(cls):
        headers_dict = cls.storage('headers', {})
        return [(key, value) for key, value in headers_dict.items()]

    @classmethod
    def get_client_header(cls, name: str, default: str = None):
        pass


    @classmethod
    def get_cookie(cls, name: str, default: str = ''):
        c = cls.STORAGE.cookies
        return c[name] if name in c else default

    @classmethod
    def request_time(cls) -> float:
        return time.time() - cls.STORAGE.time_start
