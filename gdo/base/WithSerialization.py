import importlib
import sys

import msgspec.msgpack

from gdo.base.WithPygdo import WithPygdo


class WithSerialization(WithPygdo):
    """
    GDOPack serializer.
    Uses a dict with a magic key to unmarshal objects.
    """

    MAGIC_KEY = "_GDO_"
    MAGIC_NUM = b"\xDE\xAD\xBE\xEF"

    def gdo_redis_fields(self) -> list[str]:
        """Override this to define which fields should be serialized."""
        return []

    def gdo_wake_up(self):
        """Initialize fields here if required."""
        pass

    def gdopack(self) -> bytes:
        """Serialize object with a magic prefix for fast unpacking."""
        return self.MAGIC_NUM + msgspec.msgpack.encode(self.gdopack2())

    def gdopack2(self) -> dict:
        """Convert object into a serializable dict, handling nested objects."""
        data = {self.MAGIC_KEY: f"{self.__module__}.{self.__class__.__name__}"}
        for key in self.gdo_redis_fields():
            value = getattr(self, key)
            if hasattr(value, 'gdopack2'):
                data[key] = value.gdopack2()
            elif type(value) is dict:
                data[key] = {k: v.gdopack2() if hasattr(v, 'gdopack2') else v for k, v in value.items()}
            elif isinstance(value, list):
                data[key] = [item.gdopack2() if hasattr(item, 'gdopack2') else item for item in value]
            else:
                data[key] = value

        return data

    @staticmethod
    def gdounpack(data: bytes):
        """Deserialize object and detect if it's a packed GDO."""
        is_gdo = data.startswith(WithSerialization.MAGIC_NUM)
        unpacked_data = msgspec.msgpack.decode(data[4:] if is_gdo else data)
        return WithSerialization.gdopinstances(unpacked_data) if is_gdo else unpacked_data

    @staticmethod
    def gdopinstances(dic):
        """Reconstruct objects recursively, avoiding excessive type checking."""
        dic_type = type(dic)

        if dic_type in {int, float, str, bool, bytes, bytearray} or dic is None:
            return dic

        if dic_type is list:
            return [WithSerialization.gdopinstances(item) for item in dic]

        if dic_type is dict:
            class_path = dic.get(WithSerialization.MAGIC_KEY)
            if not class_path:
                return {key: WithSerialization.gdopinstances(value) for key, value in dic.items()}
            # Restore object from class path
            module_name, class_name = class_path.rsplit(".", 1)
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = importlib.import_module(module_name)
            klass = getattr(module, class_name)
            obj = klass.__new__(klass)
            obj._blank = False

            # Initialize and set attributes
            obj.gdo_wake_up()
            for key, value in dic.items():
                setattr(obj, key, WithSerialization.gdopinstances(value))

            from gdo.base.GDO import GDO
            # if isinstance(obj, GDO):
            #     from gdo.base.Cache import Cache
            #     return Cache.obj_for(obj)
            return obj
        return dic
        