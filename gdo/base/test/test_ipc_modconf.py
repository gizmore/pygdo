import unittest
from unittest.mock import AsyncMock, MagicMock

from gdo.base.method.ipc_modconf import ipc_modconf


class IpcModuleConfigTest(unittest.IsolatedAsyncioTestCase):
    async def test_lazily_initialized_config_is_used(self):
        method = MagicMock()
        module = MagicMock(spec=['module_config', 'save_config_val'])
        module.save_config_val = AsyncMock()
        setting = MagicMock()
        setting.validate.return_value = True
        module.module_config.return_value = {'show_intro_link': setting}
        method.get_module.return_value = module
        method.param_val.side_effect = {'key': 'show_intro_link', 'value': '1'}.get
        await ipc_modconf.gdo_execute(method)
        module.module_config.assert_called_once_with()
        module.save_config_val.assert_awaited_once_with('show_intro_link', '1')

    async def test_unknown_key_is_ignored(self):
        method = MagicMock()
        module = MagicMock()
        module.module_config.return_value = {}
        method.get_module.return_value = module
        method.param_val.side_effect = {'key': 'missing', 'value': '1'}.get
        await ipc_modconf.gdo_execute(method)
        module.save_config_val.assert_not_called()
