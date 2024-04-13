class Connector:
    AVAILABLE = {}

    @classmethod
    def register(cls, klass):
        cls.AVAILABLE[klass.__name__] = klass


