from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Arrays, Files
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Template import GDT_Template
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
        from gdo.core.GDT_Select import GDT_Select
        from gdo.ui.GDT_Section import GDT_Section
        lst = [
            GDT_Section().title_raw('Core'),
            GDT_Enum('core.env').choices({'dev': 'dev', 'prod': 'prod'}).not_null().initial('dev'),
            cls.data_str('core.sitename', 'PyGDO', "Short abbrev of the site's name, like WeChall or Google."),
            cls.data_str('core.web_root', '/', 'Needs to end with a slash, E.g.: "/" or "/www/".'),
            cls.data_str('core.domain', 'localhost', "full domain for full urls in mails."),
            cls.data_int('core.port', 80, 'Plaintext HTTP port.').min(0).max(65535),
            cls.data_int('core.port_tls', 443, "Encrypted HTTPS port.").min(0).max(65535),
            cls.data_int('core.force_tls', 0, "Redirect every HTTP to HTTPS?").min(0).max(1),
            cls.data_int('core.processes', 8, 'Number of webserver processes. Needed to coordinate IPC events.').min(1).max(256),
            cls.data_int('core.json_debug', 0, 'Enable pretty JSON encoding?').min(0).max(1),
            cls.data_int('core.event_debug', 0, 'Debug events?').min(0).max(1),
            cls.data_int('core.gdt_debug', 0, 'Debug-log GDT allocations. 0-Off, 1-Classnames, 2-WithStacktrace').min(0).max(2),
            cls.data_int('core.gdo_debug', 0, 'Debug-log GDO allocations. 0-Off, 1-Classnames, 2-WithStacktrace').min(0).max(2),
            cls.data_int('core.profile', 0, 'Enable yappi Profiler?').min(0).max(1),
            cls.data_int('core.allocs', 0, 'Enable memory allocation profiler?').min(0).max(1),
            GDT_Section().title_raw('File'),
            cls.data_int('file.block_size', 4096),
            cls.data_str('file.directory', 'files/'),
            cls.data_str('file.umask', "0600"),
            cls.data_str('dir.umask', "0700"),
            cls.data_int('file.upload_max', 1024*1024*4),
            GDT_Section().title_raw('Database'),
            cls.data_str('db.host', 'localhost'),
            cls.data_int('db.port', 3306),
            cls.data_str('db.name', 'pygdo8'),
            cls.data_str('db.user', 'pygdo8'),
            cls.data_str('db.pass', 'pygdo8'),
            cls.data_int('db.debug', 0),
            GDT_Section().title_raw('Cache'),
            cls.data_int('redis.enabled', 0),
            cls.data_str('redis.uds', ""),
            cls.data_str('redis.host', 'localhost'),
            cls.data_int('redis.port', 6379),
            cls.data_int('redis.db', 0),
            GDT_Section().title_raw('Locale'),
            GDT_Select('i18n.iso').choices({'en': 'English', 'de': 'Deutsch'}).initial('en'),
            GDT_Section().title_raw('Session'),
            cls.data_str('sess.name', 'PyGDO'),
            cls.data_str('sess.same_site', 'lax'),
            GDT_Section().title_raw('Log'),
            cls.data_int('log.request', 1),
            GDT_Section().title_raw('Mail'),
            cls.data_int('mail.debug', 1),
            cls.data_str('mail.host', 'localhost'),
            cls.data_int('mail.tls', 1),
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
        gdt = GDT_String(key_path)
        if tt:
            gdt.tooltip_raw(tt, False)
        v = Arrays.walk(Application.CONFIG, key_path)
        gdt.initial(v or default)
        return gdt

    @classmethod
    def data_int(cls, key_path: str, default: int, tt: str='') -> GDT:
        from gdo.core.GDT_Int import GDT_Int
        gdt = GDT_Int(key_path).initial(str(default))
        if tt:
            gdt.tooltip_raw(tt, False)
        v = Arrays.walk(Application.CONFIG, key_path)
        if v:
            gdt.initial(str(v))
        return gdt

    @classmethod
    def rewrite(cls, path: str, data: dict[str, GDT]):
        if Files.is_file(path):
            Files.copy(path, path + ".OLD")
        out = GDT_Template.python('install', 'config.toml.html', {
            'data': data,
            'modules': ModuleLoader.instance()._cache,
            'Time': Time,
        })
        if out:
            with open(path, 'w') as fo:
                fo.write(out)

