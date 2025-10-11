from gdo.base.Application import Application
from gdo.base.ParseArgs import ParseArgs


def href(module_name: str, method_name: str, append: str = '', fmt: str = 'html'):
    splitted = ''
    new_append = ''
    if append:
        for kv in append.lstrip('&').split('&'):
            key, val = kv.split('=', 1)
            if not key.startswith('_'):
                val = val.replace(ParseArgs.ARG_SEPARATOR, ParseArgs.ESCAPED_SEPARATOR)
                splitted += f"{ParseArgs.ENTRY_SEPARATOR}{key}{ParseArgs.ARG_SEPARATOR}{val}"
            else:
                new_append += f"&{kv}"
    return f"/{module_name}.{method_name}{splitted}.{fmt}?_lang={Application.STORAGE.lang}{new_append}"


def url(module_name: str, method_name: str, append: str = '', fmt: str = 'html'):
    return Application.PROTOCOL + "://" + Application.domain() + Application.get_current_port(':') + Application.web_root() + href(module_name, method_name, append, fmt)
