import asyncio
import io
import os
from asyncio import iscoroutine
from urllib.parse import parse_qs
from multipart import parse_options_header, MultipartParser

from gdo.base.Application import Application
from gdo.base.Cache import Cache
from gdo.base.Exceptions import GDOModuleException, GDOMethodException
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Parser import WebParser
from gdo.base.Render import Mode
from gdo.base.Util import Files
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.file.GDT_FileOut import GDT_FileOut
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
        assert scope['type'] == 'http', f"Type {scope['type']} not supported."

        if FRESH:
            FRESH = False
            Application.init(os.path.dirname(__file__))
            ModuleLoader.instance().load_modules_db()
            ModuleLoader.instance().init_modules(True, True)
        else:
            GDT.GDT_MAX = 0
            GDO.GDO_MAX = 0
            GDT.GDT_COUNT = 0
            GDO.GDO_COUNT = 0
            GDT.GDT_ALIVE = 0
            GDO.GDO_ALIVE = 0
            Application.EVENT_COUNT = 0
            Application.DB_TRANSACTIONS = 0
            Application.DB_READS = 0
            Application.DB_WRITES = 0
            Logger.LINES_WRITTEN = 0
            Cache.clear_stats()
            Application.fresh_page()

        Application.init_asgi(scope)
        qs = parse_qs(scope['query_string'].decode())

        url = scope['path'] if scope['path'].lstrip('/') else '/core.welcome.html'

        scope['REQUEST_URI'] = scope['path'] + '?' + scope['query_string'].decode()

        lang = 'en'
        if '_lang' in qs:
            lang = qs['_lang'][0]
            del qs['_lang']
        Application.STORAGE.lang = lang

        path = Application.file_path(url.lstrip('/'))

        if Files.is_file(path):
            session = GDO_Session.start(False)
            user = session.get_user()
            Application.set_current_user(user)
            method = file_server().env_server(user.get_server()).env_user(user).input('_url', url)
            gdt = await method.execute()
            while iscoroutine(gdt):
                gdt = await gdt
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
                Application.set_current_user(user)
                Logger.user(user)
                method = dir_server().env_server(user.get_server()).env_user(user).input('_url', url)
            else:
                session = GDO_Session.start(True)
                user = session.get_user()
                Application.set_current_user(user)
                Application.set_session(session)
                server = user.get_server()
                channel = None
                parser = WebParser(user, server, channel, session)
                try:
                    method = parser.parse(url.lstrip('/'))
                except (GDOModuleException, GDOMethodException):
                    method = not_found().env_server(server).env_user(user).input('_url', url)

            if Application.get_request_method() == 'POST':
                body = b""
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    if message['type'] == 'http.request':
                        body += message.get('body', b'')
                        if not message.get('more_body', False):
                            break
                content_type, options = parse_options_header(Application.get_client_header('content-type'))
                if content_type == "multipart/form-data" and 'boundary' in options:
                    stream = io.BytesIO(body)
                    parser = MultipartParser(stream, options["boundary"])
                    for part in parser:
                        if part.filename:
                            method.add_file(part.name, part.filename, part.raw)
                        else:
                            qs[part.name] = part.value
                    for part in parser.parts():
                        part.close()
                else:
                    qs.update(parse_qs(body.decode()))

            result = await method.inputs(qs).execute()
            while asyncio.iscoroutine(result):
                result = await result

            if isinstance(result, GDT_FileOut):
                size = int(Application.get_header('Content-Length'))
                await send({
                    'type': 'http.response.start',
                    'status': Application.get_status_code(),
                    'headers': Application.get_headers_asgi(),
                })
                for chunk in result:
                    size -= len(chunk)
                    await send({
                        'type': 'http.response.body',
                        'body': chunk,
                        'more_body': size > 0,
                    })
                return

            if Application.is_html():
                Application.header('Content-Type', 'text/html; charset=UTF-8')
                page = Application.get_page()
                result = page.result(result).method(method)
                for module in ModuleLoader.instance().enabled():
                    module.gdo_load_scripts(page)
                    module.gdo_init_sidebar(page)

            session.save()

            out = result.render(Mode.HTML).encode()

            Application.header('Content-Length', str(len(out)))
            await send({
                'type': 'http.response.start',
                'status': Application.get_status_code(),
                'headers': Application.get_headers_asgi(),
            })
            await send({
                'type': 'http.response.body',
                'body': out,
                'more_body': False,
            })

    except Exception as ex:
        try:
            Logger.exception(ex)
            out = Application.get_page().result(GDT_Error.from_exception(ex)).method(server_error()).render(Mode.HTML)
            try:
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                })
            except:
                pass
            await send({
                'type': 'http.response.body',
                'body': out.encode(),
            })
        except Exception:
            try:
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                })
            except:
                pass
            await send({
                'type': 'http.response.body',
                'body': str(ex).encode(),
            })
