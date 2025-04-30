from gdo.base.Exceptions import GDOModuleException, GDOError
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader


class Parser:
    """
    Parse a CLI line into PyGDO Method.
    Syntax: echo 1 $(echo $(sum 2 3) will print 1 5
    """
    _user: object
    _server: object
    _channel: object
    _session: object

    def __init__(self, mode, user, server, channel, session):
        super().__init__()
        self._mode = mode
        self._user = user
        self._server = server
        self._channel = channel
        self._session = session

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
        tokens[0] = method = self.get_method(tokens[0][1:])

        for t in tokens[1:]:
            if isinstance(t, list):
                method._raw_args.add_cli_part(self.methodize(t))
            else:
                method._raw_args.add_cli_part(t)

        # Automatically click submit button in CLI
        from gdo.form.MethodForm import MethodForm
        if isinstance(method, MethodForm):
            method.cli_auto_button()

        return method

    def get_method(self, cmd: str) -> Method | None:
        method = ModuleLoader.instance().get_method(cmd)
        if not method:
            raise GDOModuleException(cmd)
        return self.decorate_method(method)

    def decorate_method(self, method: Method):
        return (method.env_user(self._user).env_server(self._server).env_channel(self._channel).
                env_session(self._session).env_mode(self._mode).env_http(False))
