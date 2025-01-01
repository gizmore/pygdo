import os
from urllib.parse import parse_qs, unquote

from gdo.base.Application import Application
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Render import Mode
from gdo.base.Util import dump, Strings, Files
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.ui.GDT_Error import GDT_Error

FRESH = True

async def app(scope, receive, send):
    try:
        global FRESH
        Logger.init(os.path.dirname(__file__)+"/protected/logs/")
        if scope['type'] == 'lifespan':
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
            return

        assert scope['type'] == 'http', f"Type {scope['type']} not supported"
        if FRESH:
            FRESH = False
            Application.init(os.path.dirname(__file__))
            ModuleLoader.instance().load_modules_db()
            ModuleLoader.instance().init_modules(True, True)
        else:
            Application.fresh_page()

        url = 'core.welcome.html'
        Application.request_method(scope['method'])
        Application.init_asgi(scope)
        qs = parse_qs(scope['query_string'].decode())
        dump(str(qs))
        dump(str(scope))

        scope['path'] = scope['path'].lstrip('/')
        url = scope['path'] if scope['path'] else 'core.welcome.html'

        scope['REQUEST_URI'] = scope['path'] + '?' + scope['query_string'].decode()
        dump(url)

        lang = 'en'
        if '_lang' in qs:
            lang = qs['_lang'][0]
            del qs['_lang']

        path = Application.file_path(url)

        if Files.is_file(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            method = file_server().env_server(user.get_server()).env_user(user).input('_url', path)
            gdt = await method.execute()
            await send({
                'type': 'http.response.start',
                'status': Application.get_status_code(),
                'headers': Application.get_headers_asgi(),
            })
            length = int(Application.get_header('Content-Length'))
            for chunk in gdt:
                length -= len(chunk)
                await send({
                    'type': 'http.response.body',
                    'body': chunk,
                    'more_body': length > 0,
                })
            return
        else:
            if Files.is_dir(path):
                session = GDO_Session.start(False)
                user = session.get_user()
                method = dir_server().env_server(user.get_server()).env_user(user).input('_url', path)
            else:
                session = GDO_Session.start(True)
                user = session.get_user()
                Application.set_current_user(user)
                Application.set_session(session)
                server = user.get_server()
                channel = None
                parser = WebParser(user, server, channel, session)
                method = parser.parse(url)
                if not method:
                    method = not_found().env_server(server).env_user(session.get_user()).input('_url', url)

            body = b""
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break

            if data := body.decode():
                qs.update(parse_qs(data))

            dump(str(qs))
            result = await method.inputs(qs).execute()

            if Application.is_html():
                page = Application.get_page()
                result = page.result(result).method(method)
                for module in ModuleLoader.instance().enabled():
                    module.gdo_load_scripts(page)
                    module.gdo_init_sidebar(page)

            out = result.render(Mode.HTML).encode()

            length = str(len(out))
            Application.header('Content-Length', length)
            await send({
                'type': 'http.response.start',
                'status': Application.get_status_code(),
                'headers': Application.get_headers_asgi(),
            })
            await send({
                'type': 'http.response.body',
                'body': out,
            })
            session.save()
    except Exception as ex:
        try:
            Logger.exception(ex)
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
