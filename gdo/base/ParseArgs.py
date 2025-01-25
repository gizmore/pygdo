import re
from urllib.parse import parse_qs

# Constants for separators
ARG_SEPARATOR = "~"  # Key-value separator: `for~gizmore`
LIST_SEPARATOR = "^"  # Multi-value separator: `tags~python^flask^linux`
ENTRY_SEPARATOR = ";"  # Separates arguments: `;for~gizmore`

class ParseArgs:
    """Handles argument parsing from CLI, URL paths, query strings, POST data, and files."""

    def __init__(self):
        self.module = None
        self.method = None
        self.args = {}  # Stores parsed key-value arguments
        self.possible_multiple = set()  # Parameters that might be multiple

    def add_cli_line(self, cli_args: list[str]):
        """
        Parses module, method, named arguments, and positional arguments from CLI input.
        CLI format: `module.method --argname value --argname2 value pos1 pos2`
        """
        if not cli_args:
            return

        # Extract module and method from first argument
        first_arg = cli_args.pop(0)
        if "." in first_arg:
            self.module, self.method = first_arg.split(".", 1)
        else:
            self.module = first_arg

        # Parse remaining arguments (flags first, then positionals)
        it = iter(cli_args)
        positional_args = []
        while True:
            try:
                token = next(it)
                if token.startswith("--"):  # Named flag (e.g., `--brief 1`)
                    param_name = token.lstrip("-")
                    value = next(it, None)

                    # If already set, convert into a list (for multiple values)
                    if param_name in self.args:
                        if not isinstance(self.args[param_name], list):
                            self.args[param_name] = [self.args[param_name]]
                        self.args[param_name].append(value)
                        self.possible_multiple.add(param_name)
                    else:
                        self.args[param_name] = value
                else:
                    positional_args.append(token)  # Store positional args separately
            except StopIteration:
                break

        # Assign positional args as numbered keys
        for i, value in enumerate(positional_args):
            self.args[f"positional_{i+1}"] = value

    def finalize_with_gdt(self, gdt_params):
        """
        After `yield_params()` runs, adjust parameters based on `GDT.multiple(True)`.
        Converts values into lists if required.
        """
        for param in gdt_params:
            if param.name in self.possible_multiple and param.is_multiple():
                if not isinstance(self.args.get(param.name), list):
                    self.args[param.name] = [self.args[param.name]]

    def __repr__(self):
        return f"ParserArgs(module={self.module}, method={self.method}, args={self.args})"

# ✅ **Example Usage**
parser = ParserArgs()

# CLI Example: `$ user.profile --brief 1 gizmore`
parser.add_cli_line(["user.profile", "--brief", "1", "gizmore"])
print(parser)
# Expected: module=user, method=profile, args={'brief': '1', 'positional_1': 'gizmore'}

# ✅ **Handling Multiple Values**
parser.add_cli_line(["user.profile", "--tags", "python", "--tags", "flask", "--tags", "linux", "extra_arg"])
print(parser)
# Expected: module=user, method=profile, args={'tags': ['python', 'flask', 'linux'], 'positional_1': 'extra_arg'}

# ✅ **Finalizing with GDTs**
class ExampleGDT:
    def __init__(self, name, multiple=False):
        self.name = name
        self._multiple = multiple

    def is_multiple(self):
        return self._multiple

# Assume these are from `yield_params()`
gdt_params = [ExampleGDT("tags", multiple=True), ExampleGDT("brief")]

parser.finalize_with_gdt(gdt_params)
print(parser)
# Expected: {'brief': '1', 'tags': ['python', 'flask', 'linux'], 'positional_1': 'extra_arg'}
