import os.path
import asyncio
import time
from io import BytesIO
from urllib.parse import parse_qs, unquote
from multipart import MultipartParser

from gdo.base.IPC import IPC
from gdo.base.ParseArgs import ParseArgs
from gdo.base.Application import Application
from gdo.base.Exceptions import GDOModuleException, GDOMethodException, GDOParamNameException
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.Method import Method
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Render import Mode
from gdo.base.Util import (Strings, Files, bytelen, html)
from gdo.base.method.client_error import client_error
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.ui.GDT_Error import GDT_Error
from gdo.base.Cache import Cache

FRESH = True
SIDEBARS = False
REQUEST_COUNT = 0

def aiorun(coro):
    while asyncio.iscoroutine(coro):
        if not Application.LOOP.is_running():
            coro = Application.LOOP.run_until_complete(coro)
        else:
            time.sleep(0.000025)
    return coro

def application(environ, start_response):
    Application.LOOP = asyncio.new_event_loop()
    return pygdo_application(environ, start_response)

def pygdo_application(environ, start_response):
    """
    The PyGDO Rendering core and http  method proxy
    """
    url = 'core.welcome.html'
    try:
        global FRESH
        global SIDEBARS
        SIDEBARS = False

        if FRESH:
            Logger.init(os.path.dirname(__file__) + "/protected/logs/")
            Application.init(os.path.dirname(__file__))
            Application.init_web(environ)
            loader = ModuleLoader.instance()
            loader.load_modules_db()
            loader.init_modules(True, True)
            from gdo.base.Trans import Trans
            Application.is_http(True)
            while Application.LOOP.is_running():
                time.sleep(0.000025)
            Application.LOOP.run_until_complete(IPC.web_register_ipc())
            FRESH = False
        else:
            Application.init_common()
            Application.init_web(environ)
            Application.init_thread(None)

        qs = parse_qs(environ['QUERY_STRING'])

        Application.request_method(environ['REQUEST_METHOD'])
        args = ParseArgs()

        if '_url' in qs:
            url = unquote(Strings.substr_from(qs['_url'][0], '/', qs['_url'][0]))
            # del qs['_url']
            if not url:
                url = 'core.welcome.html'
        elif environ['PATH_INFO'] != '/':
            url = environ['PATH_INFO'].lstrip('/')

        args.add_arg('_url', url)

        lang = 'en'
        if '_lang' in qs:
            lang = qs['_lang']
            #del qs['_lang']

        path = Application.file_path(url)

        if file := GDO_SeoFile.get_by_url(url):
            session = GDO_Session.start(False)
            user = session.get_user()
            Application.set_current_user(user)
            method = file_server().env_server(user.get_server()).env_user(user).input('_url', file.get_path())
            gdt = method.execute()
            gdt = aiorun(gdt)
            if isinstance(gdt, GDT_FileOut):
                headers = Application.get_headers()
                start_response(Application.get_status(), headers)
                for chunk in gdt:
                    yield chunk
                return
            Application.header('Content-Type', 'text/html; Charset=UTF-8')
            headers = Application.get_headers()
            start_response(Application.get_status(), headers)
            yield Application.get_page().method(method).result(gdt).render(Mode.render_html).encode()
            return
        if Files.is_file(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            method = file_server().env_server(user.get_server()).args(args).env_user(user).env_session(session)
            gdt = method.execute()
            gdt = aiorun(gdt)
            if isinstance(gdt, GDT_FileOut):
                headers = Application.get_headers()
                start_response(Application.get_status(), headers)
                for chunk in gdt:
                    yield chunk
                return
            Application.header('Content-Type', 'text/html; Charset=UTF-8')
            headers = Application.get_headers()
            start_response(Application.get_status(), headers)
            yield Application.get_page().method(method).result(gdt).render(Mode.render_html).encode()
            return
        else:
            if Files.is_dir(path):
                session = GDO_Session.start(False)
                user = session.get_user()
                server = user.get_server()
                method = dir_server().env_user(user, False).env_session(session).env_server(server)
                method._raw_args = args
            else:
                session = GDO_Session.start(True)
                user = session.get_user()
                server = user.get_server()
                args.add_path_vars(url)
                args.add_get_vars(qs)
                method = args.get_method().env_user(user).env_session(session).env_server(server)
            Application.set_current_user(user)
            Application.status("200 OK")
            if Application.config('log.request', '0') == '1':
                Logger.request(url, str(qs))
            if not method:
                method = not_found().env_server(server).env_user(session.get_user())

            if environ['REQUEST_METHOD'] == 'POST' and environ['CONTENT_TYPE'].startswith('multipart/form-data'):
                    ctype = environ.get('CONTENT_TYPE', '')
                    length = int(environ.get('CONTENT_LENGTH', 0))
                    body = environ['wsgi.input'].read(length)
                    _, params = ctype.split(";", 1)
                    boundary = params.strip().split("=", 1)[1]
                    parser = MultipartParser(BytesIO(body), boundary.encode())
                    fields = {}
                    files = {}
                    for part in parser:
                        if part.filename:
                            args.add_file(part.name, part.filename, part.raw)
                        else:
                            fields[part.name] = part.value
                    args.add_post_vars(fields)

            elif environ['REQUEST_METHOD'] == 'POST':  # POST PARAMS
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ['wsgi.input'].read(content_length)
                post_data_decoded = post_data.decode()
                post_variables = parse_qs(post_data_decoded)
                args.add_post_vars(post_variables)

            try:
                result = method.execute()
                result = aiorun(result)
            except Exception as ex:
                result = GDT_Error.from_exception(ex, method.gdo_module().render_name())

            if type(result) is GDT_FileOut:
                headers = Application.get_headers()
                start_response(Application.get_status(), headers)
                for chunk in result:
                    yield chunk
                return
            
            mode = args.get_mode()
            if mode.value < 10:
                Application.header('Content-Type', 'text/html; Charset=UTF-8')
            elif mode == Mode.render_json:
                Application.header('Content-Type', 'application/json; Charset=UTF-8')
            elif mode == Mode.render_txt:
                Application.header('Content-Type', 'text/plain; Charset=UTF-8')

            page = Application.get_page()
            result = page.result(result).method(method)
            if mode == Mode.render_html:
                page.init_sidebars()
                SIDEBARS = True

            # asyncio.gather(*Application.TASKS)
            # Application.TASKS = []

            session.save()
            headers = Application.get_headers()
            response = result.render(mode)
            if hasattr(response, 'encode'):
                response = response.encode()
            headers.extend([('Content-Length', str(len(response)))])
            start_response(Application.get_status(), headers)

            yield response
            # generator = ChunkedResponse(response)
            # yield from generator.wsgi_generator()

    except (GDOModuleException, GDOMethodException) as ex:
        yield error_page(ex, start_response, not_found(), '404 Not Found')
    except GDOParamNameException as ex:
        yield error_page(ex, start_response, client_error().exception(ex), '409 User Error')
    except Exception as ex:
        try:
            yield error_page(ex, start_response, server_error(), "500 Fatal Error", '1')
        except Exception as ex:
            Logger.exception(ex)
            msg = str(ex) + Logger.traceback(ex)
            response_headers = [
                ('Content-Type', 'text/plain; Charset=UTF-8'),
                ('Content-Length', str(bytelen(msg)))
            ]
            status = '500 PyGDO Totally Fatal Error'
            start_response(status, response_headers)
            yield msg.encode('UTF-8')


def error_page(ex, start_response, method: Method, status: str, trace: str = None):
    global SIDEBARS
    loader = ModuleLoader.instance()
    if trace:
        result = GDT_Error.from_exception(ex, method.gdo_module().render_name())
    else:
        result = GDT_Error().title_raw(method.gdo_module().render_name()).text_raw(str(ex))
    page = Application.get_page()
    if not SIDEBARS:
        for module in loader.enabled():
            module.gdo_init_sidebar(page)
    response_body = page.method(method).result(result).render(Mode.render_html)
    response_headers = [
        ('Content-Type', 'text/html; Charset=UTF-8'),
        ('Content-Length', str(bytelen(response_body)))
    ]
    start_response(status, response_headers)
    return response_body.encode('UTF-8')
