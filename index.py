import asyncio
import cgi
import os.path
import traceback
from urllib.parse import parse_qs, unquote

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException, GDOMethodException, GDOParamNameException
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Render import Mode
from gdo.base.Util import (Strings, Files, dump, bytelen, err)
from gdo.base.method.client_error import client_error
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.ui.GDT_Error import GDT_Error

FRESH = True


def application(environ, start_response):
    return pygdo_application(environ, start_response)

def pygdo_application(environ, start_response):
    """
    The PyGDO Rendering core and http  method proxy
    """
    url = 'core.welcome.html'
    try:
        global FRESH
        GDT.GDT_MAX = 0
        GDO.GDO_MAX = 0
        GDT.GDT_COUNT = 0
        GDO.GDO_COUNT = 0
        GDT.GDT_ALIVE = 0
        GDO.GDO_ALIVE = 0
        Application.DB_TRANSACTIONS = 0
        Logger.LINES_WRITTEN = 0
        if FRESH:
            Logger.init(os.path.dirname(__file__) + "/protected/logs/")
            Application.init(os.path.dirname(__file__))
            Application.init_common()
            Application.init_web(environ)
            loader = ModuleLoader.instance()
            loader.load_modules_db()
            loader.init_modules(True, True)
            Application.is_http(True)
            FRESH = False
        else:
            Application.init_common()
            Application.init_web(environ)
            Application.fresh_page()

        qs = parse_qs(environ['QUERY_STRING'])

        Application.request_method(environ['REQUEST_METHOD'])

        if '_url' in qs:
            url = unquote(Strings.substr_from(qs['_url'][0], '/'))
            # get_params = parse_qs(url)
            del qs['_url']
            if not url:
                url = 'core.welcome.html'

        lang = 'en'
        if '_lang' in qs:
            lang = qs['_lang']
            del qs['_lang']

        path = Application.file_path(url)

        if Files.is_file(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            method = file_server().env_server(user.get_server()).env_user(user).env_session(session).input('_url', url)
            gdt = method.execute()
            while asyncio.iscoroutine(gdt):
                gdt = asyncio.run(gdt)
            headers = Application.get_headers()
            start_response(Application.get_status(), headers)
            if isinstance(gdt, GDT_FileOut):
                for chunk in gdt:
                    yield chunk
                return
            yield gdt.render(Mode.HTML).encode()
            return
        else:
            session = GDO_Session.start(True)
            user = session.get_user()
            Logger.user(user)
            Application.set_current_user(user)
            Application.set_session(session)
            Application.status("200 OK")
            server = user.get_server()
            channel = None
            if Files.is_dir(path):
                session = GDO_Session.start(False)
                method = dir_server().env_user(user, False).env_session(session).env_server(server).input('_url', url)
            else:
                parser = WebParser(user, server, channel, session)
                method = parser.parse(url)
            if not method:
                method = not_found().env_server(server).env_user(session.get_user()).input('_url', url)

            method.inputs(qs)  # GET PARAMS
            #method._message = Message(f"${method.gdo_trigger()}", Mode.HTML).env_copy(method)

            if environ['REQUEST_METHOD'] == 'POST' and environ['CONTENT_TYPE'].startswith('multipart/form-data'):
                post_variables = cgi.FieldStorage(
                    fp=environ['wsgi.input'],
                    environ=environ,
                    keep_blank_values=True
                )
                fields = {}
                for var in post_variables:
                    if filename := post_variables[var].filename:
                        method.add_file(var, filename, post_variables[var].value)
                    else:
                        fields[var] = post_variables[var].value
                method.inputs(fields)

            elif environ['REQUEST_METHOD'] == 'POST':  # POST PARAMS
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ['wsgi.input'].read(content_length)
                post_data_decoded = post_data.decode('utf-8')
                post_variables = parse_qs(post_data_decoded)
                method.inputs(post_variables)

            try:
                result = method.execute()
            except Exception as ex:
                err('%s', [str(ex)])
                err('%s', [traceback.format_exc()])
                result = method

            while asyncio.iscoroutine(result):
                result = asyncio.run(result)

            if isinstance(result, GDT_FileOut):
                headers = Application.get_headers()
                start_response(Application.get_status(), headers)
                for chunk in result:
                    yield chunk
                return

            if Application.is_html():
                Application.header('Content-Type', 'text/html; Charset=UTF-8')
            elif Application.get_mode() == Mode.JSON:
                Application.header('Content-Type', 'application/json; Charset=UTF-8')
            elif Application.get_mode() == Mode.TXT:
                Application.header('Content-Type', 'text/plain; Charset=UTF-8')

            if Application.is_html():
                page = Application.get_page()
                result = page.result(result).method(method)
                for module in ModuleLoader.instance().enabled():
                    module.gdo_load_scripts(page)
                    module.gdo_init_sidebar(page)

            session.save()
            response = result.render(Application.get_mode())
            headers = Application.get_headers()
            headers.extend([('Content-Length', str(bytelen(response)))])
            start_response(Application.get_status(), headers)
            if isinstance(response, str):
                yield response.encode('utf-8')
            else:
                yield response
    except (GDOModuleException, GDOMethodException) as ex:
        yield error_page(ex, start_response, not_found().input('_url', url), '404 Not Found', False)
    except GDOParamNameException as ex:
        yield error_page(ex, start_response, client_error().exception(ex), '409 User Error', False)
    except Exception as ex:
        try:
            yield error_page(ex, start_response, server_error(), "500 Fatal Error", True)
        except Exception as ex:
            msg = str(ex) + traceback.format_exc()
            response_headers = [
                ('Content-Type', 'text/html; Charset=UTF-8'),
                ('Content-Length', str(bytelen(msg)))
            ]
            status = '500 PyGDO Totally Fatal Error'
            start_response(status, response_headers)
            yield msg.encode('UTF-8')


def error_page(ex, start_response, method: Method, status: str, trace: bool = True):
    loader = ModuleLoader.instance()
    if trace:
        result = GDT_Error.from_exception(ex)
    else:
        result = GDT_Error().title_raw('PyGDO').text_raw(str(ex))
    page = Application.get_page()
    for module in loader._cache.values():
        module.gdo_load_scripts(page)
        module.gdo_init_sidebar(page)
    response_body = page.method(method).result(result).render(Mode.HTML)
    response_headers = [
        ('Content-Type', 'text/html; Charset=UTF-8'),
        ('Content-Length', str(bytelen(response_body)))
    ]
    start_response(status, response_headers)
    return response_body.encode('UTF-8')
