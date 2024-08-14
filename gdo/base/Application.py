import os
import sys
import threading
import time
import tomlkit

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_Session import GDO_Session

from gdo.base.Events import Events
from gdo.base.Logger import Logger
from gdo.base.Render import Mode
from gdo.base.Util import Arrays, dump


class Application:
    RUNNING = True
    PROTOCOL = 'http'
    IS_HTTP = False
    LOADER: object
    EVENTS: 'Events'
    # SERVER: object  # This server instance is the server for the GHOST user :/
    STORAGE = threading.local()
    LANG_ISO = 'en'
    TIME = time.time()
    DB_READS: int = 0
    DB_WRITES: int = 0

    # DB: object
    PATH: str = ''
    CONFIG_PATH: str = ''
    CONFIG: dict[str, str] = {}

    @classmethod
    def tick(cls):
        t = time.time()
        cls.TIME = round(t, 6)
        cls.STORAGE.time_start = t
        cls.EVENTS.update_timers(cls.TIME)

    @classmethod
    def is_http(cls, is_http: bool):
        cls.IS_HTTP = is_http

    @classmethod
    def init(cls, path, config_file: str = 'protected/config.toml'):
        from gdo.base.ModuleLoader import ModuleLoader
        # Cache.init()
        cls.PATH = os.path.normpath(path) + '/'
        os.environ['TZ'] = 'UTC'
        time.tzset()
        cls.LOADER = ModuleLoader()
        cls.EVENTS = Events()
        config_path = 'protected/config_test.toml' if 'unittest' in sys.modules.keys() else config_file
        config_path = os.path.join(cls.PATH, config_path)
        cls.CONFIG_PATH = config_path
        cls.get_page().init()
        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                cls.CONFIG = tomlkit.load(f)
                cls.init_thread(None)
        else:
            from gdo.install.Config import Config
            cls.CONFIG = Config.defaults()
        Application.init_common()

    @classmethod
    def reset(cls):
        cls.get_page().init()

    @classmethod
    def has_db(cls):
        return cls.db() is not None

    @classmethod
    def file_path(cls, path: str = ''):
        return os.path.join(cls.PATH, path)

    @classmethod
    def temp_path(cls, path: str = ''):
        return cls.file_path('temp/' + path)

    @classmethod
    def set_current_user(cls, user):
        cls.STORAGE.user = user
        cls.STORAGE.lang = user.get_lang_iso()

    @classmethod
    def fresh_page(cls):
        from gdo.ui.GDT_Page import GDT_Page
        cls.STORAGE.page = GDT_Page()
        return cls.STORAGE.page

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
        cls.init_thread(None)
        cls.STORAGE.time_start = float(environ.get('mod_wsgi.request_start')) / 1000000.0
        cls.STORAGE.environ = environ
        cls.STORAGE.headers = {}
        cls.init_cookies(environ)
        cls.STORAGE.ip = environ.get('REMOTE_ADDR')
        cls.PROTOCOL = environ['REQUEST_SCHEME']
        # cls.SERVER = GDO_Server.get_by_connector('Web')

    @classmethod
    def init_common(cls):
        cls.STORAGE.mode = Mode.HTML
        cls.tick()
        cls.DB_READS = 0
        cls.DB_WRITES = 0
        Logger.init()
        cls.init_thread(None)
        # Logger.debug("Application.init_common()")
        cls.STORAGE.user = None
        cls.STORAGE.lang = 'en'

    @classmethod
    def init_thread(cls, thread):
        from gdo.base.Database import Database
        if thread:
            Logger.debug(f'Init thread {thread.name}')
        cls.STORAGE.user = None
        cls.STORAGE.time_start = cls.TIME
        cls.mode(Mode.HTML)
        cls.STORAGE.lang = 'en'
        if 'db' in cls.CONFIG:
            cfg = cls.CONFIG['db']
            cls.STORAGE.DB = Database(cfg['host'], cfg['name'], cfg['user'], cfg['pass'])

    @classmethod
    def db(cls):
        return cls.STORAGE.DB

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
        return cls.storage('status', "200 GDO OK")

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
    def get_client_header(cls, name: str, default: str = None) -> str | None:
        env = cls.STORAGE.environ
        return env[name] if name in env else default

    @classmethod
    def get_cookie(cls, name: str, default: str = ''):
        c = cls.STORAGE.cookies
        return c[name] if name in c else default

    @classmethod
    def request_time(cls) -> float:
        return time.time() - cls.STORAGE.time_start

    @classmethod
    def environ(cls, key: str) -> str:
        return cls.STORAGE.environ[key]

    @classmethod
    def current_href(cls) -> str:
        return cls.environ('REQUEST_URI')

    @classmethod
    def set_session(cls, session: 'GDO_Session'):
        cls.STORAGE.session = session

    @classmethod
    def get_session(cls) -> 'GDO_Session':
        return cls.STORAGE.session

    @classmethod
    def has_session(cls):
        return hasattr(cls.STORAGE, 'session')

    @classmethod
    def is_unit_test(cls):
        return 'unittest' in sys.modules.keys()

    @classmethod
    def domain(cls) -> str:
        return cls.config('core.domain', 'pygdo.localhost')

    @classmethod
    def web_root(cls) -> str:
        return cls.config('core.web_root', '/')
