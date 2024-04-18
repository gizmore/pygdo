import magic
import os
from urllib.parse import parse_qs

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException, GDOModuleException
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Util import Files, Strings
from gdo.core.method.not_found import not_found
from gdo.ui.GDT_Error import GDT_Error

is_fresh: bool = True


def handler(request):
    global is_fresh
    loader = ModuleLoader.instance()
    if is_fresh:
        is_fresh = False
        Application.init(os.path.dirname(__file__))
        loader.load_modules_db()
        loader.init_modules()

    qs = parse_qs(request.args)
    url = 'core.welcome.html'
    file = ''
    if '_url' in qs:
        url = qs['_url'][0]
        file = Strings.substr_to(url, '?', url)
        file = Application.file_path(file)

    if file and Files.exists(file):
        Files.serve_filename(file, request)
        return 0

    request.content_type = 'text/html'
    page = Application.get_page()

    page._method = not_found()
    try:
        parser = WebParser(request, url)
        method = parser.parse()
        page._method = method
        post_data = parse_qs(request.read().decode('UTF-8'))

        method.inputs(post_data or {})
        result = method.execute()
    except GDOMethodException as ex:
        result = page._method.init_params({'_url': url}).user(parser._user).execute()
    except GDOModuleException as ex:
        result = GDT_Error().title_raw('Core').text('err_module', [ex._module])
    except Exception as ex:
        result = GDT_Error.from_exception(ex)

    page.result(result)

    if Application.is_html():
        for module in loader._cache.values():
            module.gdo_load_scripts(page)
            module.gdo_init_sidebar(page)

    request.write(page.render_html())
    return 0
