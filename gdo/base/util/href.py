from gdo.base.Application import Application
from urllib.parse import parse_qsl, quote, urlencode


def _segment(value: str) -> str:
    """Encode a point-separated URL segment; points are route separators."""
    return quote(str(value), safe='').replace('.', '%2E')


def href(module_name: str, method_name: str, append: str = '', fmt: str = 'html', positional: tuple|list = ()):
    """Build ``module.method.positional.option.value.format`` URLs.

    ``append`` remains a convenient API for existing callers. Normal entries
    become option/value pairs in the filename; only technical ``_`` entries
    remain query parameters.
    """
    technical = []
    options = []
    for key, value in parse_qsl(append.lstrip('&'), keep_blank_values=True) if append else []:
        if key.startswith('_'):
            technical.append((key, value))
        else:
            options.extend((key, value))
    if not any(key == '_lang' for key, _value in technical):
        technical.append(('_lang', Application.STORAGE.lang))
    parts = [module_name, method_name, *map(_segment, positional), *map(_segment, options), fmt]
    return f"/{'.'.join(parts)}?{urlencode(technical, doseq=True)}"


def url(module_name: str, method_name: str, append: str = '', fmt: str = 'html', positional: tuple|list = ()):
    return Application.PROTOCOL + "://" + Application.domain() + Application.get_current_port(':') + Application.web_root() + href(module_name, method_name, append, fmt, positional)
