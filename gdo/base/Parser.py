from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException, GDOParamNameException
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import Strings, err, err_raw, dump
from gdo.core.GDT_Repeat import GDT_Repeat


class Parser:
    """
    Parse a CLI line into PyGDO Method.
    Syntax: echo 1 $(echo $(sum 2 3) will print 15
    TODO: Method nesting!
    """
    _line: str
    _user: object
    _is_web: bool  # Do not care yet

    def __init__(self, line: str, user):
        super().__init__()
        self._line = line
        self._user = user
        self._is_web = False

    def parse(self):
        lines = self.split_commands(self._line)
        methods = []
        for line in lines:
            method = self.parse_line(line)
            methods.append(method)
        # TODO: make method chain. methods have method._next_method to chain
        return methods[0] if len(methods) else None

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
        method = self.get_method(tokens[0])
        if not method:
            raise GDOModuleException(tokens[0])
        method.env_user(self._user)
        self.start_session(method)
        parser = method.get_arg_parser(self._is_web)
        args, unknown_args = parser.parse_known_args(tokens[1:])
        for gdt in method.parameters().values():
            val = args.__dict__[gdt.get_name()] or ''
            val = val.rstrip()
            if isinstance(gdt, GDT_Repeat):  # There may be one GDT_Repeat per method, which is the last param. append an array
                vals = [val]
                vals.extend(unknown_args)
                gdt.val(vals)
            else:
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

    def get_method(self, cmd: str) -> Method | None:
        return ModuleLoader.instance().get_method(cmd)

    def start_session(self, method: Method):
        method.cli_session()


class WebParser(Parser):
    _url: str

    def __init__(self, url, user):
        self._url = url
        # self._session = GDO_Session.start()
        # self._user = self._session.get_user()
        # Application.set_current_user(self._user)
        Application.mode(Mode.HTML)
        super().__init__(self.build_line(self._url), user)
        self._is_web = True

    def build_line(self, url: str) -> str:
        """
        Builds a CLI command line from a web url
        """
        qa = url.split('?', 1)
        line = qa[0]
        ext = Strings.rsubstr_from(line, '.')
        try:
            Application.mode(Mode[ext.upper()])
        except KeyError as ex:
            err('err_render_mode', [ext.upper()])
        line = Strings.rsubstr_to(line, '.')  # remove extension
        parts = line.split(';')
        cmd = parts[0]  # command part
        self.get_method(cmd)  # Check early, else 404 is not shown -.-
        for part in parts[1:]:
            try:
                parts = part.split('.', 1)
                param_name, param_value = parts
                cmd += f" --{param_name}=\"{param_value}\""
            except ValueError:
                raise GDOParamNameException(cmd, line)
        return cmd

    # def write(self, s):
    #     self._request.write(s)

    def get_method(self, cmd: str) -> Method | None:
        try:
            loader = ModuleLoader.instance()
            mod_method = Strings.substr_to(cmd, ';', cmd)
            module_name = Strings.substr_to(mod_method, '.')
            method_name = Strings.substr_from(mod_method, '.')
            return loader._cache[module_name].get_method(method_name)
        except KeyError:
            err_raw('Unknown Module ' + cmd)
            return None

    def start_session(self, method: Method):
        pass  # Do nothing in web parser
