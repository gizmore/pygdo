class WithMsgpackSupport:
    def to_dict(self) -> dict[str, any]:
        return {
            key: value.to_dict() if isinstance(value, WithMsgpackSupport) else value
            for key, value in self.__dict__.items()
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        obj = cls.__new__(cls)
        for key, value in data.items():
            setattr(obj, key, value)
        return obj
