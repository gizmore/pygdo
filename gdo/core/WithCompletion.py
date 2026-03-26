class WithCompletion:
    _completion_href: str

    def completion(self, href: str):
        self._completion_href = href
        return self

    def html_autocomplete(self) -> str:
        return f' gdo-autocomplete="{self._completion_href}"'
