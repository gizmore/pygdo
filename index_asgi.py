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
from gdo.base.IPC import IPC
from gdo.base.Logger import Logger
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.ParseArgs import ParseArgs
from gdo.base.Render import Mode
from gdo.base.Util import Files, jsn
from gdo.base.method.dir_server import dir_server
from gdo.base.method.file_server import file_server
from gdo.base.method.server_error import server_error
from gdo.core.GDO_Session import GDO_Session
from gdo.core.method.not_found import not_found
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdo.file.GDT_FileOut import GDT_FileOut
from gdo.ui.GDT_Error import GDT_Error


def display_top_malloc(snapshot, f, limit=200, key_type='lineno'):
    import tracemalloc, linecache
    # snapshot = snapshot.filter_traces((
    #     tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
    #     tracemalloc.Filter(False, "<unknown>"),
    # ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit, file=f)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024), file=f)
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line, file=f)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024), file=f)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024), file=f)


async def app(scope, receive, send):
    try:
        Application.LOOP = asyncio.get_running_loop()
        Logger.init(os.path.dirname(__file__)+"/protected/logs/")
        if scope['type'] == 'lifespan':
            message = await receive()
            if message['type'] == 'lifespan.startup':
                Application.init(os.path.dirname(__file__))
                #PYPP#START#
                if Application.config('core.allocs') == '1':
                    import tracemalloc
                    tracemalloc.start()
                if Application.config('core.imports') == '1':
                    from gdo.base.ImportTracker import ImportTracker
                    ImportTracker.enable()
                if Application.config('core.profile') == '1':
                    import yappi
                    yappi.start()
                #PYPP#END#
                ModuleLoader.instance().load_modules_db()
                ModuleLoader.instance().init_modules(True, True)
                await IPC.web_register_ipc()
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
            return
        if scope['type'] == 'http':
            #PYPP#START#
            GDT.GDT_MAX = 0
            GDO.GDO_MAX = 0
            GDT.GDT_COUNT = 0
            GDO.GDO_COUNT = 0
            GDT.GDT_ALIVE = 0
            GDO.GDO_ALIVE = 0
            IPC.COUNT = 0
            Application.EVENT_COUNT = 0
            Application.DB_TRANSACTIONS = 0
            Application.DB_READS = 0
            Application.DB_WRITES = 0
            Logger.LINES_WRITTEN = 0
            Cache.clear_stats()
            #PYPP#END#
            Application.init_common()
            Application.init_asgi(scope)
            Application.tick()

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
            elif file := GDO_SeoFile.get_by_url(url):
                session = GDO_Session.start(False)
                user = session.get_user()
                Application.set_current_user(user)
                method = file_server().env_server(user.get_server()).env_user(user).input('_url', file.get_path())
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
                args = ParseArgs()
                if Files.is_dir(path):
                    session = GDO_Session.start(False)
                    user = session.get_user()
                    Application.set_current_user(user)
                    method = dir_server().env_server(user.get_server()).env_user(user).input('_url', url)
                else:
                    session = GDO_Session.start(True)
                    user = session.get_user()
                    Application.set_current_user(user)
                    if Application.config('log.request', '0') == '1':
                        asyncio.ensure_future(Logger.arequest(url, str(qs)))
                    Application.set_session(session)
                    server = user.get_server()
                    channel = None
                    # args = ParseArgs()
                    args.add_path_vars(url)
                    args.add_get_vars(qs)
                    try:
                        method = args.get_method()
                        await IPC.web_check_for_ipc()
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
                        qs = {}
                        for part in parser:
                            if part.filename:
                                args.add_file(part.name, part.filename, part.raw)
                            else:
                                qs[part.name] = part.value
                        for part in parser.parts():
                            part.close()
                        args.add_post_vars(qs)
                    else:
                        args.add_post_vars(parse_qs(body.decode()))

                method._raw_args = args
                method.env_user(user).env_session(session).env_server(user.get_server())
                result = await method.execute()
                while asyncio.iscoroutine(result):
                    result = await result

                if type(result) is GDT_FileOut:
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

                mode = args.get_mode()
                page = Application.get_page()
                if Application.get_mode() == Mode.render_html:
                    Application.header('Content-Type', 'text/html; charset=UTF-8')
                    for module in ModuleLoader.instance().enabled():
                        module.gdo_init_sidebar(page)
                    result = page.result(result).method(method).render_html()
                elif mode.is_html():
                    result = page.result(result).method(method).render_html()
                    Application.header('Content-Type', 'text/html; charset=UTF-8')
                elif mode == Mode.render_json:
                    result = jsn(page.result(result).method(method).render_json())
                    Application.header('Content-Type', 'application/json; Charset=UTF-8')
                elif mode == Mode.render_txt:
                    result = page.result(result).method(method).render_txt()
                    Application.header('Content-Type', 'text/plain; Charset=UTF-8')

                session.save()
                out = result.encode()

                Application.header('Content-Length', str(len(out)))
                await send({
                    'type': 'http.response.start',
                    'status': Application.get_status_code(),
                    'headers': Application.get_headers_asgi(),
                })

                # generator = ChunkedResponse(out)
                # async for chunk, more_body in generator.asgi_generator():
                #     await send({
                #         'type': 'http.response.body',
                #         'body': chunk,
                #         'more_body': more_body,
                #     })

                await send({
                    'type': 'http.response.body',
                    'body': out,
                })

                #PYPP#START#
                if Application.config('core.allocs', '0') == '1':
                    if qs.get('__yappi', None):
                        import tracemalloc
                        with open(Application.file_path('temp/yappi_mem.log'), 'a') as f:
                            snapshot = tracemalloc.take_snapshot()
                            display_top_malloc(snapshot, f)

                if Application.config('core.imports') == '1':
                    if qs.get('__yappi', None):
                        from gdo.base.ImportTracker import ImportTracker
                        ImportTracker.write_to_file(Application.file_path('temp/yappi_imports.log'))
                        ImportTracker.reset()

                if Application.config('core.profile', '0') == '1':
                    if qs.get('__yappi', None):
                        import yappi
                        with open(Application.file_path('temp/yappi.log'), 'a') as f:
                            yappi.get_func_stats().print_all(out=f, columns={
                                0: ("name", 64),
                                1: ("ncall", 12),
                                2: ("tsub", 8),
                                3: ("ttot", 8),
                                4: ("tavg", 8)})
                #PYPP#END#

    except Exception as ex:
        try:
            Logger.exception(ex)
            out = Application.get_page().result(GDT_Error.from_exception(ex)).method(server_error()).render(Mode.render_html)
            try:
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                })
            except Exception as ex3:
                Logger.exception(ex3)
            await send({
                'type': 'http.response.body',
                'body': out.encode(),
            })
        except Exception as ex4:
            trace = Logger.traceback(ex4)
            try:
                await send({
                    'type': 'http.response.start',
                    'status': 500,
                })
            except Exception as ex2:
                Logger.exception(ex2)
            await send({
                'type': 'http.response.body',
                'body': f"{str(ex)}\n{trace}".encode(),
            })
