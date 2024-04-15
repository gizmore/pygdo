import sys

from gdo.base import module_base
from gdo.base.Method import Method


class version(Method):

    def __init__(self):
        super().__init__()

    def execute(self):
        return self.message('msg_version', [sys.version, str(module_base.instance().CORE_VERSION)])

