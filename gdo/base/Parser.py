import argparse

from gdo.base.Method import Method
from gdo.base.Util import Strings
from gdo.core.GDO_User import GDO_User
from gdo.core.method.echo import echo


class Parser:

    _line: str
    _last: Method
    _user: GDO_User

    def __init__(self, line: str, user):
        super().__init__()
        self._line = line
        self._user = user

    def parse(self):
        lines = self._line.split('&&')
        methods = []
        for line in lines:
            methods.append(self.parse_line(line))
        return methods[0]

    def parse_line(self, line: str) -> Method:
        command = Strings.substr_to(line, ' ', line)
        argline = Strings.substr_from(line, ' ', '')
        method = self.get_method(command)
        method.user(self._user)
        parser = argparse.ArgumentParser(description=method.gdo_render_descr(), usage=method.gdo_render_usage())
        args, unknown_args = parser.parse_known_args(argline.split(" "))
        return method

    def get_method(self, cmd: str) -> Method:
        return echo()

