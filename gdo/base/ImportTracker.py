import builtins
import inspect
import threading
import json
from collections import defaultdict


class ImportTracker:

    _real_import = builtins.__import__
    _data = defaultdict(lambda: {
        "count": 0,
        "locations": defaultdict(int),
    })
    _lock = threading.Lock()
    _enabled = False

    @staticmethod
    def _called_inside_function():
        frame = inspect.currentframe()
        try:
            frame = frame.f_back
            while frame:
                code = frame.f_code
                if code.co_name != "<module>":
                    return frame
                frame = frame.f_back
        finally:
            del frame
        return None

    @staticmethod
    def _hook(name, globals=None, locals=None, fromlist=(), level=0):
        frame = ImportTracker._called_inside_function()

        if frame:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            location = f"{filename}:{lineno}"

            with ImportTracker._lock:
                entry = ImportTracker._data[name]
                entry["count"] += 1
                entry["locations"][location] += 1

        return ImportTracker._real_import(name, globals, locals, fromlist, level)

    @classmethod
    def enable(cls):
        if not cls._enabled:
            builtins.__import__ = cls._hook
            cls._enabled = True

    @classmethod
    def disable(cls):
        if cls._enabled:
            builtins.__import__ = cls._real_import
            cls._enabled = False

    @classmethod
    def report(cls):
        return {
            mod: {
                "count": data["count"],
                "locations": dict(data["locations"]),
            }
            for mod, data in sorted(cls._data.items(), key=lambda x: -x[1]["count"])
        }

    @classmethod
    def write_to_file(cls, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cls.report(), f, indent=2, sort_keys=True)

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._data.clear()
