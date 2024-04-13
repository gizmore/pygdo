import argparse

from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.core.method.echo import echo


class Parser:

    _line: str
    _last: Method

    def __init__(self, line):
        super().__init__()
        self._line = line

    def parse(self):
        lines = self._line.split('&&')
        for line in lines:
            method = self.parse_line(line)

    def parse_line(self, line: str) -> Method:
        command = Strings.substr_to(line, ' ', line)
        argline = Strings.substr_from(line, ' ', '')
        method = self.get_method(command)
        parser = argparse.ArgumentParser(description=method.gdo_render_descr(), usage=method.gdo_render_usage())
        args, unknown_args = parser.parse_known_args(argline.split(" "))
        return method

    def get_method(self, cmd: str) -> Method:
        return echo()

