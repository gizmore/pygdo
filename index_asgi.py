import os
from urllib.parse import parse_qs, unquote

from gdo.base.Application import Application
from gdo.base.Message import Message
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Render import Mode
from gdo.base.Util import dump, Strings, Files
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.core.method.welcome import welcome
from gdo.ui.GDT_Error import GDT_Error
from gdo.ui.GDT_Success import GDT_Success

FRESH = True

async def app(scope, receive, send):
    try:
        global FRESH
        assert scope['type'] == 'http'
        if FRESH:
            FRESH = False
            Application.init(os.path.dirname(__file__))
            ModuleLoader.instance().load_modules_db()
        else:
            Application.fresh_page()

        ModuleLoader.instance().init_modules(True, True)

        url = 'core.welcome.html'
        Application.request_method(scope['method'])
        Application.init_asgi(scope)
        qs = parse_qs(scope['query_string'])
        dump(str(qs))
        dump(str(scope))

        url = scope['path'] if scope['path'] else 'core.welcome.html'

        # if '_url' in qs:
        #     url = unquote(Strings.substr_from(qs['_url'][0], '/'))
        #     # get_params = parse_qs(url)
        #     del qs['_url']
        #     if not url:
        #         url = 'core.welcome.html'

        dump(url)

        lang = 'en'
        if '_lang' in qs:
            lang = qs['_lang']
            del qs['_lang']

        path = Application.file_path(url)

        if Files.is_file(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            method = file_server().env_server(user.get_server()).env_user(user).input('_url', path)
            gdt = await method.execute()
            # headers = Application.get_headers()
            # start_response(Application.get_status(), headers)
            # for chunk in gdt:
            #     yield chunk
        elif Files.is_dir(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            method = dir_server().env_server(user.get_server()).env_user(user).input('_url', path)

        else:
            session = GDO_Session.start(True)
            Application.set_current_user(session.get_user())
            Application.set_session(session)
            # Application.status("200 OK")
            user = session.get_user()
            server = user.get_server()
            channel = None
            parser = WebParser(user, server, channel, session)
            method = parser.parse(url)
            if not method:
                method = not_found().env_server(server).env_user(session.get_user()).input('_url', url)
            # method._message = Message(f"${method.gdo_trigger()}", Mode.HTML).env_copy(method)

        body = b""
        header = b""
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break

        # Process the received body
        data = body.decode("utf-8")

        result = await method.execute()

        if Application.is_html():
            page = Application.get_page()
            result = page.result(result).method(method)
            for module in ModuleLoader.instance().enabled():
                module.gdo_load_scripts(page)
                module.gdo_init_sidebar(page)

        out = result.render(Mode.HTML)

        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': Application.get_headers_asgi(),
        })

        await send({
            'type': 'http.response.body',
            'body': out.encode(),
        })

    except Exception as ex:
        try:
            out = Application.get_page().result(GDT_Error.from_exception(ex)).method(server_error()).render(Mode.HTML)
            await send({
                'type': 'http.response.start',
                'status': 500,
            })
            await send({
                'type': 'http.response.body',
                'body': out.encode(),
            })
        except Exception:
            await send({
                'type': 'http.response.start',
                'status': 500,
            })
            await send({
                'type': 'http.response.body',
                'body': str(ex).encode(),
            })
