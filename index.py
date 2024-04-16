import os
from urllib.parse import parse_qs

import magic

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOMethodException
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Util import Files
from gdo.core.method.not_found import not_found
from gdo.ui.GDT_Page import GDT_Page

is_fresh: bool = True


def handler(request):
    global is_fresh
    if is_fresh:
        is_fresh = False
        Application.init(os.path.dirname(__file__))
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules()

    qs = parse_qs(request.args)
    url = 'core.welcome'
    if '_url' in qs:
        url = qs['_url'][0]

    if Files.exists(url):
        mime = magic.Magic(mime=True)
        request.content_type = mime.from_file(url)
        with open(url) as fi:
            request.write(fi.read())
        return 0

    request.content_type = 'text/html'

    parser = WebParser(request, url)
    try:
        method = parser.parse()
        result = method.execute()
    except GDOMethodException as ex:
        result = not_found().init_params({'_url': url}).user(parser._user).execute()

    page = GDT_Page().result(result)
    request.write(page.render_html())
    return 0
