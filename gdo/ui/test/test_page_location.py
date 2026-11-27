import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from gdo.base.WithModuleConfig import WithModuleConfig
from gdo.ui.GDT_PageLocation import GDT_PageLocation


class PageLocationTest(unittest.IsolatedAsyncioTestCase):
    async def test_save_page_location_and_none(self):
        page = MagicMock()
        field = GDT_PageLocation('birthday_position').not_null().initial('_none')
        module = WithModuleConfig()
        module._module_config = {'birthday_position': field}
        module.get_id = MagicMock(return_value=1)
        module.get_name = MagicMock(return_value='birthday')
        row = MagicMock()
        with patch('gdo.ui.GDT_PageLocation.Application.get_page', return_value=page), \
             patch('gdo.base.GDO_ModuleVal.GDO_ModuleVal.blank', return_value=row) as blank, \
             patch('gdo.base.Application.Application.publish_event_async', new_callable=AsyncMock), \
             patch('gdo.base.IPC.IPC.send'):
            await module.save_config_val('birthday_position', '_left_bar')
            self.assertEqual('_left_bar', blank.call_args.args[0]['mv_val'])
            self.assertIs(page._left_bar, field.get_value())
            await module.save_config_val('birthday_position', '_none')
            self.assertEqual('_none', blank.call_args.args[0]['mv_val'])
            self.assertIsNone(field.get_value())

    def test_choice_label_still_round_trips(self):
        field = GDT_PageLocation('position').not_null()
        with patch('gdo.ui.GDT_PageLocation.Application.get_page', return_value=MagicMock()):
            self.assertEqual('_left_bar', field.to_val(field.to_value('Left')))
