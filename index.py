import json
import os
from urllib.parse import parse_qs

from mod_python import Cookie, apache
from gdo.base.Application import Application
from gdo.base.Parser import WebParser
from gdo.core.GDO_Session import GDO_Session

is_fresh: bool = True


def handler(req):
    global is_fresh
    if is_fresh:
        is_fresh = False
        Application.init(os.path.dirname(__file__))


    session = GDO_Session.start(Cookie.get_cookies(req))
    parser = WebParser(req.args, session)
    req.content_type = 'text/plain'
    get = parse_qs(req.args)

    req.write(json.dumps(get['_url'].__class__.__str__()))

    return apache.OK
