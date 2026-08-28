from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.core import module_core


class clear_cache(Method):
    """
    Clear all caches. Uses an Event to allow others to clean up as well
    """
    def gdo_user_permission(self) -> str | None:
        return 'staff'

    @classmethod
    def gdo_trigger(cls) -> str:
        return "cc"

    async def gdo_execute(self) -> GDT:
        # Resolve the response before clearing the language cache.
        message = t('msg_cache_cleared')
        if mc := module_core.instance():
            if mc.is_persisted():
                await mc.save_config_val('av', str(int(mc.cfg_asset_version()) + 1))
        Cache.clear()
        await Application.EVENTS.publish('clear_cache')
        return self.empty(message)
