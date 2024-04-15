import json
import os
from mod_python import apache
from gdo.base.Application import Application

is_fresh: bool = True


def handler(req):
    global is_fresh
    if is_fresh:
        is_fresh = False
        Application.init(os.path.dirname(__file__))
    req.content_type = 'text/plain'
    req.write(json.dumps(req.args))
    req.write("Hello, World!" + Application.DB.__str__())
    return apache.OK
