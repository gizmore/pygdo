import argparse
import json
import re
from urllib.parse import parse_qs

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import Strings
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Repeat import GDT_Repeat
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.echo import echo


class Parser:
    _line: str
    _user: GDO_User

    def __init__(self, line: str, user):
        super().__init__()
        self._line = line
        self._user = user

    def parse(self):
        lines = self.split_commands(self._line)
        methods = []
        for line in lines:
            method = self.parse_line(line)
            methods.append(method)
        return methods[0]

    def split_commands(self, input_string):
        commands = []
        current_command = ''
        inside_quotes = False

        for char in input_string:
            if char == '"':
                inside_quotes = not inside_quotes
            elif char == '&' and not inside_quotes:
                if current_command.strip() != '':
                    commands.append(current_command.strip())
                    current_command = ''
                continue
            current_command += char

        if current_command.strip() != '':
            commands.append(current_command.strip())

        return commands

    def parse_line(self, line: str) -> Method:
        tokens = self.tokenize(line)
        # command = Strings.substr_to(line, ' ', line)
        # argline = Strings.substr_from(line, ' ', '')
        method = self.get_method(tokens[0])
        if not method:
            raise GDOModuleException(tokens[0])
        method.user(self._user)
        self.start_session(method)
        parser = argparse.ArgumentParser(description=method.gdo_render_descr(), usage=method.gdo_render_usage())
        for gdt in method.parameters().values():
            if gdt.is_positional():
                parser.add_argument(gdt.get_name())
            else:
                parser.add_argument(f'--{gdt.get_name()}', default=gdt.get_initial())
        try:
            args, unknown_args = parser.parse_known_args(tokens[1:])
            for gdt in method.parameters().values():
                val = args.__dict__[gdt.get_name()]
                if isinstance(gdt, GDT_Repeat):
                    val += " " + " ".join(unknown_args)
                gdt.val(val)
        except Exception as ex:
            method.error('%s', [str(ex)])
        return method

    def tokenize(self, line: str):
        tokens = []
        current_token = ''
        inside_quotes = False

        for char in line:
            if char == ' ' and not inside_quotes:
                # If not inside quotes and encounter a space, finish the current token
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            elif char == '"':
                # Toggle inside_quotes flag when encountering a quote
                inside_quotes = not inside_quotes
            else:
                # Add character to the current token
                current_token += char

        # Add the last token if there is any
        if current_token:
            tokens.append(current_token)

        return tokens

    def get_method(self, cmd: str) -> Method:
        return ModuleLoader.instance()._methods[cmd]

    def start_session(self, method: Method):
        method.cli_session()


class WebParser(Parser):
    _url: str
    _user: object
    _request: object
    _session: GDO_Session

    def __init__(self, req, url):
        self._url = url
        self._request = req
        self._session = GDO_Session.start(req)
        self._user = self._session.get_user()
        Application.set_current_user(self._user)
        Application.mode(Mode.HTML)
        super().__init__(self.build_line(self._url), self._session.get_user())

    def build_line(self, url: str) -> str:
        """
        Builds a CLI command line from a web url
        """
        qa = url.split('?', 1)
        line = qa[0]
        ext = Strings.rsubstr_from(line, '.')
        Application.mode(Mode[ext.upper()])
        line = Strings.rsubstr_to(line, '.')  # remove extension
        parts = line.split(';')
        cmd = parts[0]  # command part
        for part in parts[1:]:
            try:
                param_name, param_value = part.split('.', 1)
                cmd += f" --{param_name}=\"{param_value}\""
            except ValueError:
                pass
        return cmd

    def write(self, s):
        self._request.write(s)

    def get_method(self, cmd: str) -> Method | None:
        try:
            loader = ModuleLoader.instance()
            mod_method = Strings.substr_to(cmd, ';', cmd)
            module_name = Strings.substr_to(mod_method, '.')
            method_name = Strings.substr_from(mod_method, '.')
            return loader._cache[module_name].get_method(method_name)
        except KeyError:
            return None

    def start_session(self, method: Method):
        pass
