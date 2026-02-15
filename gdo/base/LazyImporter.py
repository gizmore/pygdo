import importlib


class LazyImporter:
    _import_line_cache = {}  # import_line -> returned object

    @classmethod
    def import_once(cls, line: str, inject_globals: dict | None = None):
        cached = cls._import_line_cache.get(line)
        if cached is not None:
            if inject_globals is not None:
                cls._inject_from_line(line, cached, inject_globals)
            return cached

        pkg = inject_globals.get("__package__") if inject_globals else None

        if line.startswith("import "):
            target = line[len("import ") :].strip()
            modname, asname = cls._parse_as(target)
            mod = importlib.import_module(modname)
            ret = mod
            if inject_globals is not None:
                inject_globals[asname or modname.split(".")[-1]] = mod

        elif line.startswith("from "):
            rest = line[len("from ") :].strip()
            src, sep, tail = rest.partition(" import ")
            if not sep:
                raise ValueError(f"Invalid import line: {line!r}")

            what = tail.strip()
            name, asname = cls._parse_as(what)

            src_mod = importlib.import_module(src, package=pkg)

            if name == "*":
                ret = src_mod
            else:
                obj = getattr(src_mod, name)
                ret = obj
                if inject_globals is not None:
                    inject_globals[asname or name] = obj
        else:
            raise ValueError(f"Unsupported import line: {line!r}")

        cls._import_line_cache[line] = ret
        return ret

    @staticmethod
    def _parse_as(s: str):
        parts = s.split()
        if len(parts) == 1:
            return parts[0], None
        if len(parts) == 3 and parts[1] == "as":
            return parts[0], parts[2]
        raise ValueError(f"Unsupported import form: {s!r}")

    @classmethod
    def _inject_from_line(cls, line: str, ret, g: dict):
        if line.startswith("import "):
            target = line[len("import ") :].strip()
            modname, asname = cls._parse_as(target)
            g[asname or modname.split(".")[-1]] = ret
        elif line.startswith("from "):
            rest = line[len("from ") :].strip()
            _, _, tail = rest.partition(" import ")
            name, asname = cls._parse_as(tail.strip())
            if name != "*":
                g[asname or name] = ret

    @classmethod
    def reset(cls):
        cls._import_line_cache.clear()
