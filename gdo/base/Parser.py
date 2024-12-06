from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException, GDOParamNameException, GDOError
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import Strings, err, err_raw, dump


class Parser:
    """
    Parse a CLI line into PyGDO Method.
    Syntax: echo 1 $(echo $(sum 2 3) will print 15
    """
    _user: object
    _server: object
    _channel: object
    _session: object
    _is_http: bool

    def __init__(self, mode, user, server, channel, session):
        super().__init__()
        self._mode = mode
        self._user = user
        self._server = server
        self._channel = channel
        self._session = session
        self._is_http = False

    def parse(self, line: str) -> Method:
        line = line.strip()
        lines = self.split_commands(line)
        methods = []
        for line in lines:
            method = self.parse_line(line)
            methods.append(method)
        # TODO: make method chain. methods have method._next_method to chain
        return methods[0] if len(methods) else None

    def split_commands(self, line):
        commands = []
        current_command = ''
        inside_quotes = False
        i = 0
        ln = len(line)
        while i < ln:
            char = line[i]
            i += 1
            if char == '"':
                inside_quotes = not inside_quotes
                current_command += char
            elif char == '&' and line[i] == '&' and not inside_quotes:
                i += 1
                commands.append(current_command.strip())
                current_command = ''
            else:
                current_command += char
        commands.append(current_command)
        return commands

    def parse_line(self, line: str) -> Method:
        tokens = self.tokenize(line)
        tokens = self.methodize(tokens)
        return tokens

    def tokenize(self, line: str):
        """
        Parse a line into nested tokens.
        """
        inside_quotes = False
        bracket_open = 0
        token_level = 0
        curr_tokens = []
        tokens = [curr_tokens]
        current_token = '\x00'
        i = 0
        j = len(line)
        while i < j:
            char = line[i]
            i += 1
            if char == ' ' and not inside_quotes:
                if current_token:
                    curr_tokens.append(current_token)
                    current_token = ''
            elif char == '\\':
                current_token += line[i]
                i += 1
            elif char == '"':
                inside_quotes = not inside_quotes
            elif char == ')' and not inside_quotes and bracket_open:
                if current_token:
                    curr_tokens.append(current_token)
                current_token = ''
                new = curr_tokens
                del tokens[token_level]
                token_level -= 1
                curr_tokens = tokens[token_level]
                curr_tokens.append(new)
                bracket_open -= 1
            elif char == '$' and not inside_quotes and current_token == '' and line[i] == '(':
                bracket_open += 1
                token_level += 1
                i += 1
                current_token = '\x00'
                curr_tokens = []
                tokens.append(curr_tokens)
            else:
                current_token += char

        if current_token:
            curr_tokens.append(current_token)

        if token_level != 0:
            raise GDOError('err_parse_token_depth')

        return curr_tokens

    def methodize(self, tokens: list) -> Method:
        """
        Turn the tokens into a method tree and apply args
        """
        tokens[0] = self.get_method(tokens[0][1:])

        # Automatically click submit button in CLI
        from gdo.form.MethodForm import MethodForm
        if not self._is_http and isinstance(tokens[0], MethodForm):
            tokens[0].cli_auto_button()

        for t in tokens[1:]:
            if isinstance(t, list):
                tokens[0].arg(self.methodize(t))
            else:
                tokens[0].arg(t)

        return tokens[0]

    def get_method(self, cmd: str) -> Method | None:
        method = ModuleLoader.instance().get_method(cmd)
        if not method:
            raise GDOModuleException(cmd)
        return self.decorate_method(method)

    def decorate_method(self, method: Method):
        if method is None:
            return None
        return (method.env_user(self._user).env_server(self._server).env_channel(self._channel).env_session(self._session).
                env_mode(self._mode).env_http(self._is_http))


class WebParser(Parser):

    def __init__(self, user, server, channel, session):
        super().__init__(Mode.HTML, user, server, channel, session)
        self._is_http = True

    def parse(self, url: str):
        return super().parse(self.build_line(url))

    def build_line(self, url: str) -> str:
        """
        Builds a CLI command line from a web url
        """
        qa = url.split('?', 1)
        line = qa[0]
        ext = Strings.rsubstr_from(line, '.')
        try:
            mode = Mode[ext.upper()]
            self._mode = mode
            Application.mode(mode)
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
                cmd += f' --{param_name} "{param_value}"'
            except ValueError:
                raise GDOParamNameException(cmd, line)
        return cmd

    def get_method(self, cmd: str) -> Method | None:
        try:
            loader = ModuleLoader.instance()
            mod_method = Strings.substr_to(cmd, ';', cmd)
            module_name = Strings.substr_to(mod_method, '.')
            method_name = Strings.substr_from(mod_method, '.')
            method = loader._cache[module_name].get_method(method_name)
            return super().decorate_method(method)
        except KeyError:
            raise GDOModuleException(Strings.html(cmd))
