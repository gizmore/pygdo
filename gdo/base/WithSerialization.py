import importlib

import msgpack


class WithSerialization:
    """
    GDOPack serializer.
    Abuses dict with a magic key to unmarshal objects.
    """

    MAGIC_KEY = "__GDT__"

    def gdo_wake_up(self):
        """
        Init fields here if required.
        """
        pass

    def gdopack(self) -> bytes:
        return msgpack.dumps(self.gdopack2())

    def gdopack2(self) -> dict[str, any]:
        data = {}
        data[self.MAGIC_KEY] = f"{self.__module__}.{self.__class__.__name__}"
        for key, value in self.__dict__.items():
            if isinstance(value, WithSerialization):
                data[key] = value.gdopack2()
            elif isinstance(value, list):
                data[key] = [item.gdopack2() if isinstance(item, WithSerialization) else item for item in value]
            else:
                data[key] = value
        return data

    @classmethod
    def gdounpack(cls, data: bytes):
        dic = msgpack.loads(data)
        return cls.gdopinstances(dic)

    @classmethod
    def gdopinstances(cls, dic: dict):
        if isinstance(dic, (int, float, str, bool)) or dic is None:
            return dic
        if isinstance(dic, list):
            return [cls.gdopinstances(item) for item in dic]
        if not (class_path := dic.pop(cls.MAGIC_KEY, None)):
            return {key: cls.gdopinstances(value) for key, value in dic.items()}
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)
        obj = klass.__new__(klass)
        obj.gdo_wake_up()
        for key, value in dic.items():
            setattr(obj, key, cls.gdopinstances(value) if isinstance(value, (dict, list)) else value)
        return obj
