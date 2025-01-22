import sys

from gdo.base import module_base
from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String


class version(Method):

    def gdo_trigger(self) -> str:
        return 'version'

    def gdo_needs_authentication(self) -> bool:
        return False

    def execute(self):
        return GDT_String('result').text('msg_version', (sys.version, str(module_base.instance().CORE_REV)))
