class WithCompletion:
    _completion_href: str

    def completion(self, href: str):
        self._completion_href = href
        return self

    def has_completion(self) -> bool:
        return hasattr(self, '_completion_href')
