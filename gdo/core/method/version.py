import sys

from gdo.base import module_base
from gdo.base.Method import Method
from gdo.core.GDT_String import GDT_String


class version(Method):

    def __init__(self):
        super().__init__()

    def execute(self):
        return GDT_String('result').text('msg_version', [sys.version, str(module_base.instance().CORE_VERSION)])

