import os.path
from urllib.parse import parse_qs, unquote

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException, GDOMethodException, GDOParamNameException
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Render import Mode
from gdo.base.Util import (Strings, Files, dump, bytelen)
from gdo.base.method.client_error import client_error
from gdo.base.method.fileserver import fileserver
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.ui.GDT_Error import GDT_Error

FRESH = True


def application(environ, start_response):
    """
    The PyGDO Rendering core and http  method proxy
    """
    url = 'core.welcome.html'
    try:
        global FRESH
        if FRESH:
            FRESH = False
            Application.init(os.path.dirname(__file__))
            Application.init_web(environ)
            loader = ModuleLoader.instance()
            loader.load_modules_db()
            loader.init_modules()
        else:
            Application.init_common()
            Application.init_web(environ)
            loader = ModuleLoader.instance()
            Application.fresh_page()
        qs = parse_qs(environ['QUERY_STRING'])
        if '_url' in qs:
            url = unquote(Strings.substr_from(qs['_url'][0], '/'))
            if not url:
                url = 'core.welcome.html'
        session = GDO_Session.start()
        if Files.is_file(Application.file_path(url)):
            gdt = fileserver().user(session.get_user()).inputs({'_url': Application.file_path(url)}).execute()
            headers = Application.get_headers()
            start_response(Application.get_status(), headers)
            for chunk in gdt:
                yield chunk
        else:
            Application.status(200)
            parser = WebParser(url)
            method = parser.parse()
            if not method:
                method = not_found().user(session.get_user()).inputs({'_url': url})

            if environ['REQUEST_METHOD'] == 'POST':
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ['wsgi.input'].read(content_length)
                post_data_decoded = post_data.decode('utf-8')
                post_variables = parse_qs(post_data_decoded)
                method.inputs(post_variables)

            result = method.execute()

            if Application.is_html():
                page = Application.get_page()
                result = page.result(result).method(method)
                for module in loader._cache.values():
                    module.gdo_load_scripts(page)
                    module.gdo_init_sidebar(page)
            response = result.render(Application.get_mode())
            headers = Application.get_headers()
            if Application.is_html():
                headers.extend([('Content-Type', 'text/html; Charset=UTF-8')])
            elif Application.get_mode() == Mode.JSON:
                headers.extend([('Content-Type', 'application/json; Charset=UTF-8')])
            elif Application.get_mode() == Mode.TXT:
                headers.extend([('Content-Type', 'text/plain; Charset=UTF-8')])
            headers.extend([('Content-Length', str(bytelen(response)))])
            start_response(Application.get_status(), headers)
            yield response.encode('utf-8')
    except GDOModuleException as ex:
        yield error_page(ex, start_response, not_found().inputs({'_url': url}), False)
    except GDOMethodException as ex:
        yield error_page(ex, start_response, not_found().inputs({'_url': url}), False)
    except GDOParamNameException as ex:
        yield error_page(ex, start_response, client_error().exception(ex), False)
    except Exception as ex:
        try:
            yield error_page(ex, start_response, server_error())
        except Exception as ex:
            msg = str(ex)
            response_headers = [
                ('Content-Type', 'text/html; Charset=UTF-8'),
                ('Content-Length', str(bytelen(msg)))
            ]
            status = '500 PyGDO Fatal Error'
            start_response(status, response_headers)
            yield msg.encode('UTF-8')


def error_page(ex, start_response, method: Method, trace: bool = True):
    loader = ModuleLoader.instance()
    if trace:
        result = GDT_Error.from_exception(ex)
    else:
        result = GDT_Error().title_raw('PyGDO').text_raw(str(ex))
    page = Application.get_page()
    response_body = page.method(method).result(result).render(Mode.HTML)
    for module in loader._cache.values():
        module.gdo_load_scripts(page)
        module.gdo_init_sidebar(page)
    response_headers = [
        ('Content-Type', 'text/html; Charset=UTF-8'),
        ('Content-Length', str(bytelen(response_body)))
    ]
    status = '500 PyGDO Fatal Error'
    start_response(status, response_headers)
    return response_body.encode('UTF-8')
