import builtins, inspect, threading, json, importlib
from collections import defaultdict


class ImportTracker:
    _real_import = builtins.__import__
    _data = defaultdict(lambda: {"count": 0, "locations": defaultdict(int)})
    _lock = threading.Lock()
    _enabled = False

    @classmethod
    def _find_user_frame(cls):
        tracker_file = __file__
        f = inspect.currentframe()
        try:
            f = f.f_back  # caller of _find_user_frame
            while f:
                fn = f.f_code.co_filename

                # skip module-level
                if f.f_code.co_name == "<module>":
                    f = f.f_back
                    continue

                # skip our own tracker file
                if fn == tracker_file:
                    f = f.f_back
                    continue

                # skip import machinery / stdlib importlib bootstrapping
                if "/importlib/" in fn or fn.endswith(("_bootstrap.py", "_bootstrap_external.py")):
                    f = f.f_back
                    continue

                return f
                # (optional: also skip site-packages if you only want your project)
        finally:
            del f
        return None

    @staticmethod
    def _resolve_key(name, globals, fromlist, level):
        if name:
            return name
        # relative import like: from . import x
        pkg = ""
        if globals and isinstance(globals, dict):
            pkg = globals.get("__package__") or globals.get("__name__") or ""
        fl = ",".join(fromlist) if fromlist else ""
        # keep it stable + informative
        return f"{pkg} (rel{level}:{fl})"

    @classmethod
    def _hook(cls, name, globals=None, locals=None, fromlist=(), level=0):
        frame = cls._find_user_frame()
        key = cls._resolve_key(name, globals, fromlist, level)

        if frame:
            location = f"{frame.f_code.co_filename}:{frame.f_lineno}"
            with cls._lock:
                e = cls._data[key]
                e["count"] += 1
                e["locations"][location] += 1

        return cls._real_import(name, globals, locals, fromlist, level)

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
            mod: {"count": d["count"], "locations": dict(d["locations"])}
            for mod, d in sorted(cls._data.items(), key=lambda x: -x[1]["count"])
        }

    @classmethod
    def write_to_file(cls, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cls.report(), f, indent=2)

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._data.clear()
