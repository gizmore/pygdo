class WithNullable:

    _not_null: bool

    def is_not_null(self) -> bool:
        return hasattr(self, '_not_null') and self._not_null

    def not_null(self, not_null: bool = True):
        self._not_null = not_null
        return self

    def validate_null(self, val: str | None, value: any) -> bool:
        if value is None:
            if self._not_null:
                return self.error_not_null()
        return True

    def error_not_null(self):
        suggestions = self.render_suggestion()
        if suggestions:
            return self.error('err_not_null', (self.render_suggestion(),))
        else:
            return self.error('err_not_null_no_suggestions')
