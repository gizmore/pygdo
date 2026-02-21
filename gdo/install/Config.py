from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Arrays, Files
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Template import GDT_Template
from gdo.core.GDT_Token import GDT_Token
from gdo.date.Time import Time


class Config:
    """
    Create and update config.toml files.
    Setup default configuration
    """

    @classmethod
    def defaults(cls):
        gdts = cls.data({})
        return Arrays.map_dict_values_only(lambda gdt: gdt.get_val(), gdts)

    @classmethod
    def data(cls, cfg: dict) -> dict[str, GDT]:
        from gdo.ui.GDT_Section import GDT_Section
        from gdo.core.GDT_Select import GDT_Select
        lst = [
            GDT_Section().title_raw('Core and Debug'),
            GDT_Enum('core.env').choices({'dev': 'dev', 'test': 'test', 'prod': 'prod'}).not_null().initial('dev'),
            cls.data_str('core.sitename', 'PyGDO', "Short abbrev of the site's name, like WeChall or Google."),
            cls.data_str('core.web_root', '/', 'Needs to end with a slash, E.g.: "/" or "/www/".'),
            cls.data_str('core.domain', 'localhost', "full domain for full urls in mails."),
            cls.data_str('core.secret', GDT_Token.random(32), "Secret used in token calculations."),
            cls.data_int('core.port', 80, 'Plaintext HTTP port.').min(0).max(65535),
            cls.data_int('core.port_tls', 443, "Encrypted HTTPS port.").min(0).max(65535),
            cls.data_int('core.force_tls', 0, "Redirect every HTTP to HTTPS? 0/1").min(0).max(1),
            cls.data_int('core.processes', 8, 'Number of webserver processes. Needed to coordinate IPC events.').min(1).max(256),
            cls.data_int('core.pypp', 0, 'Enable pypp preprocessor? 0/1').min(0).max(1),
            GDT_Section().title_raw('Locales'),
            GDT_Select('i18n.iso').choices({'en': 'English', 'de': 'Deutsch'}).initial('en'),
            GDT_Section().title_raw('Debug'),
            cls.data_int('debug.db', 0, 'Global DB Debug. 0=off, 1=query, 2=stacktrace'),
            cls.data_int('debug.json', 0, 'Enable pretty JSON encoding? 0/1').min(0).max(1),
            cls.data_int('debug.events', 0, 'Debug events? 0/1').min(0).max(1),
            cls.data_int('debug.gdt', 0, 'Debug-log GDT allocations. 0-Off, 1-Classnames, 2-WithStacktrace').min(0).max(2),
            cls.data_int('debug.gdo', 0, 'Debug-log GDO allocations. 0-Off, 1-Classnames, 2-WithStacktrace').min(0).max(2),
            cls.data_int('debug.profiler', 0, 'Enable yappi Profiler? 0/1').min(0).max(1),
            cls.data_int('debug.memory', 0, 'Enable memory allocation profiler? 0/1').min(0).max(1),
            cls.data_int('debug.imports', 0, 'Enable Lazy Import Tracker? 0/1').min(0).max(1),
            GDT_Section().title_raw('Files'),
            cls.data_str('file.mode.dir', "0o0700", 'Mode for creating directories.'),
            cls.data_str('file.mode.file', "0o0600",'Mode for creating files.'),
            cls.data_int('file.upload_max', 1024*1024*4, 'Max upload size in bytes.'),
            cls.data_int('file.block_size', 4096, "Blocksize for chunked data.").min(512).max(2**23),
            GDT_Section().title_raw('Directories'),
            cls.data_str('dir.files', 'files/', 'Directory for storing GDO_File contents. Only allowed by token.'),
            cls.data_str('dir.assets', 'assets/', 'Directory for generated assets. Allowed'),
            cls.data_str('dir.temp', 'temp/', 'Directory for temporary files. Never allowed.'),
            cls.data_str('dir.cache', 'temp/cache/', 'Directory for cache files. Never allowed.'),
            cls.data_str('dir.logs', 'protected/logs/', 'Directory for logfiles. Never allowed.'),
            cls.data_str('dir.config', 'protected/', 'Directory for this config. Never allowed.'),
            GDT_Section().title_raw('Database (MySQL)'),
            cls.data_str('db.host', 'localhost'),
            cls.data_int('db.port', 3306),
            cls.data_str('db.name', 'pygdo8'),
            cls.data_str('db.user', 'pygdo8'),
            cls.data_str('db.pass', 'pygdo8'),
            GDT_Section().title_raw('Cache'),
            cls.data_int('redis.enabled', 0),
            cls.data_str('redis.uds', ""),
            cls.data_str('redis.host', 'localhost'),
            cls.data_int('redis.port', 6379),
            cls.data_int('redis.db', 0),
            cls.data_int('redis.zlib_level', 3).min(-1).max(9),
            GDT_Section().title_raw('Session'),
            cls.data_str('sess.name', 'PyGDO'),
            cls.data_str('sess.same_site', 'lax'),
            GDT_Section().title_raw('Log'),
            cls.data_int('log.request', 1, '0/1').min(0).max(1),
            GDT_Section().title_raw('Mail'),
            cls.data_int('mail.debug', 1).min(0).max(1),
            cls.data_str('mail.host', 'localhost'),
            cls.data_int('mail.tls', 1).min(0).max(1),
            cls.data_int('mail.port', 587),
            cls.data_str('mail.user', 'pygdo@localhost'),
            cls.data_str('mail.pass', 'pygdo'),
            cls.data_str('mail.sender', 'pygdo@localhost'),
            cls.data_str('mail.sender_name', 'PyGDO System'),
            cls.data_str('mail.errors_to', 'errors@pygdo.com'),
        ]
        dic = {}
        for gdt in lst:
            dic[gdt.get_name()] = gdt
        return dic

    @classmethod
    def data_str(cls, key_path: str, default: str, tt: str='') -> GDT:
        from gdo.core.GDT_String import GDT_String
        gdt = GDT_String(key_path).not_null()
        if tt:
            gdt.tooltip_raw(tt, False)
        v = Arrays.walk(Application.CONFIG, key_path)
        gdt.initial(v or default)
        return gdt

    @classmethod
    def data_int(cls, key_path: str, default: int, tt: str='') -> GDT:
        from gdo.core.GDT_Int import GDT_Int
        gdt = GDT_Int(key_path).initial(str(default)).not_null()
        if tt:
            gdt.tooltip_raw(tt, False)
        v = Arrays.walk(Application.CONFIG, key_path)
        if v:
            gdt.initial(str(v))
        return gdt

    @classmethod
    def rewrite(cls, path: str, data: dict[str, GDT]):
        out = GDT_Template.python('install', 'config.toml.html', {
            'data': data,
            'modules': ModuleLoader.instance()._cache,
            'Time': Time,
        })
        if out:
            with open(path, 'w', encoding='UTF-8') as fo:
                fo.write(out)
