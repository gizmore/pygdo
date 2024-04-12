import sys

from gdo.base.Method import Method


class version(Method):

    def __init__(self):
        super().__init__()

    def execute(self):
        return self.message_raw(sys.version)

