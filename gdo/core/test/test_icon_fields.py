from gdo.base.Render import Mode
from gdo.date.GDT_Timezone import GDT_Timezone
from gdo.ui.IconUTF8 import IconUTF8
from gdo.user.GDT_Gender import GDT_Gender
from gdotest.TestUtil import GDOTestCase


class IconFieldTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__) + '/../../../')
        Application.init_cli()

    def test_gender_and_timezone_have_utf8_icons(self):
        self.assertEqual('⚥', GDT_Gender('gender').render_icon(Mode.render_cli))
        self.assertEqual('🕰', GDT_Timezone('timezone').render_icon(Mode.render_cli))

    def test_every_utf8_icon_has_a_font_awesome_mapping(self):
        from gdo.icon_fa.IconFA import IconFA
        self.assertEqual(set(IconUTF8.MAP()), set(IconFA.MAP()))
import os

from gdo.base.Application import Application
