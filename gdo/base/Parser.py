import argparse

from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Repeat import GDT_Repeat


class Parser:

    _line: str
    _last: Method
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
        method.user(self._user)
        parser = argparse.ArgumentParser(description=method.gdo_render_descr(), usage=method.gdo_render_usage())
        for gdt in method.parameters().values():
            if gdt.is_positional():
                parser.add_argument(gdt.get_name())
            else:
                parser.add_argument(f'--{gdt.get_name()}', default=gdt.get_initial())
        args, unknown_args = parser.parse_known_args(tokens[1:])
        for gdt in method.parameters().values():
            val = args.__dict__[gdt.get_name()]
            if isinstance(gdt, GDT_Repeat):
                val += " " + " ".join(unknown_args)
            gdt.val(val)
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
