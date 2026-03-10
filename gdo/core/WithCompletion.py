class WithCompletion:
    _completion_href: str

    def completion(self, href: str):
        self._completion_href = href
        return self

    def html_autocomplete(self) -> str:
        if not self.has_completion(): return ''
        return ''
