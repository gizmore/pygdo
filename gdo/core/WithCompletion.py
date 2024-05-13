class WithCompletion:
    _completion_href: str

    def completion(self, href: str):
        self._completion_href = href
        return self