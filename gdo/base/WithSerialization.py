import importlib

import msgpack


class WithSerialization:
    MAGIC_KEY = "__GDT__"

    def gdopack(self) -> bytes:
        return msgpack.dumps(self.gdopack2())

    def gdopack2(self) -> dict[str, any]:
        data = {
            key: value.gdopack2() if isinstance(value, WithSerialization) else value
            for key, value in self.__dict__.items()
        }
        data[self.MAGIC_KEY] = f"{self.__module__}.{self.__class__.__name__}"  # Store class as string
        return data

    @classmethod
    def gdounpack(cls, data: bytes):
        dic = msgpack.loads(data)
        return cls.gdopinstances(dic)

    @classmethod
    def gdopinstances(cls, dic: dict):
        class_path = dic.pop(cls.MAGIC_KEY, None)  # Extract class path
        if not class_path:
            return dic  # Return raw dict if no class info
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)
        obj = klass.__new__(klass)  # Create an instance without calling __init__
        for key, value in dic.items():
            if isinstance(value, dict) and cls.MAGIC_KEY in value:
                value = cls.gdopinstances(value)  # Recursively restore nested objects
            setattr(obj, key, value)
        return obj
