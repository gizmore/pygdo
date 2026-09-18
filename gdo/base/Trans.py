import glob
import os
import re
from contextlib import contextmanager
from contextvars import ContextVar

import msgspec.json
import tomlkit

from gdo.base.Application import Application
from gdo.base.Render import Mode, Render
from gdo.base.Util import Strings, dump

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


def t(key: str, args: tuple=None):
    return Trans.tiso(Application.get_lang_iso(), key, args)


def tusr(user: 'GDO_User', key: str, args: tuple = None):
    return Trans.tiso(user.get_lang_iso(), key, args)


def tiso(iso: str, key: str, args: tuple = None):
    return Trans.tiso(iso, key, args)


def thas(key: str) -> bool:
    return Trans.has(key)


def sitename() -> str:
    return t('sitename')


class Trans:

    TRIGGER: ContextVar[str] = ContextVar('translation_trigger', default='$')

    @staticmethod
    @contextmanager
    def message_context(server=None, channel=None):
        """Snapshot the destination prefix; restore it across nested/async work."""
        trigger = channel.get_trigger() if channel is not None else None
        if trigger is None and server is not None:
            trigger = server.get_trigger()
        token = Trans.TRIGGER.set(trigger if trigger is not None else '$')
        try:
            yield
        finally:
            Trans.TRIGGER.reset(token)

    REGEX_BOLD = re.compile(r'\*\*(.+?)\*\*')

    """
    Speed optimized i18n.
    """
    EN: dict[str, str] = {}
    CACHE = {
        'en': EN,
    }

    new_iso: str

    def __init__(self, iso: str):
        self.new_iso = iso
        self.token = None

    def __enter__(self):
        self.token = Application.set_lang_iso(self.new_iso)

    def __exit__(self, *args):
        Application.reset_lang_iso(self.token)

    @staticmethod
    def init():
        Trans._load()

    @staticmethod
    def reload():
        Trans.EN = {}
        Trans.CACHE = { 'en': Trans.EN }
        Trans.init()

    @staticmethod
    def _load():
        pattern = os.path.join(Application.file_path('gdo/'), "**", "lang", "**", "*.toml")
        for lang_file in glob.glob(pattern, recursive=True):
            Trans._load_file(lang_file)

    @staticmethod
    def _load_file(lang_file: str):
        iso = Strings.rsubstr_from(lang_file, 'lang/')
        iso = iso[-7:-5]
        if iso not in Trans.CACHE:
            Trans.CACHE[iso] = {}
        with open(lang_file, 'r', encoding='UTF-8') as fd:
            more = tomlkit.load(fd)
            cache = Trans.CACHE[iso]
            for k, v in more.items():
                cache[k] = str(v)
            # Trans.CACHE[iso].update(more)

    @staticmethod
    def t(key: str, args: tuple=None):
        return Trans.tiso(Application.get_lang_iso(), key, args)

    @staticmethod
    def tiso(iso: str, key: str, args: tuple = None):
        if iso == 'bot':
            return msgspec.json.encode({'key':key, 'args': args})
        return Trans.replace_output(Trans.tiso2(iso, key, args))

    @staticmethod
    def replace_output(text: str, mode: Mode = None) -> str:
        text = text.replace('$t$', Trans.TRIGGER.get())
        mode = mode or Application.get_mode()
        return Trans.REGEX_BOLD.sub(lambda m: Render.bold(m.group(1), mode), text)

    @staticmethod
    def tiso2(iso: str, key: str, args: tuple = None):
        try:
            cache = Trans.CACHE.get(iso, Trans.EN)
            if format := cache.get(key, Trans.EN.get(key)):
                return format % args if args else format
        except:
            pass
        return key + str(args) if args else key or ''

    @staticmethod
    def has(key: str) -> bool:
        cache = Trans.CACHE.get(Application.get_lang_iso(), Trans.EN)
        return key in cache or key in Trans.EN
