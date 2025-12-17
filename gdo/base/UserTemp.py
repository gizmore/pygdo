from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from gdo.core.GDO_User import GDO_User


from gdo.ui.GDT_Bar import GDT_Bar
from gdo.base.GDT import GDT


class UserTemp:
    EMPTY_BAR = GDT_Bar().vertical()
    _cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_for_user(cls, user: 'GDO_User') -> dict[str, Any]:
        if user.get_id() not in cls._cache:
            cls._cache[user.get_id()] = {}
        return cls._cache[user.get_id()]

    @classmethod
    def get_cached_for_user(cls, user: 'GDO_User', key: str, default: Any = None) -> Any:
        return cls.get_for_user(user).get(key, default)

    @classmethod
    def clear_for_user(cls, user: 'GDO_User', key: str = None) -> None:
        cache = cls.get_for_user(user)
        if not key:
            cache.clear()
        elif key in cache:
            del cache[key]

    @classmethod
    def flash(cls, user: 'GDO_User', gdt: GDT):
        cache = cls.get_for_user(user)
        if not (flash := cache.get('flash')):
            cache['flash'] = flash = GDT_Bar().vertical()
        flash.add_field(gdt)
