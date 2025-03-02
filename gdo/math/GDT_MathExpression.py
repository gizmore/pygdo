import math
import re

from gdo.base.Application import Application
from gdo.base.Util import html
from gdo.core.GDT_RestOfText import GDT_RestOfText


class GDT_MathExpression(GDT_RestOfText):
    """
    A math expression to evaluate.
    """

    def get_namespace(self) -> dict:
        return {
            'for': 'for',
            'in': 'for',
            'pi': math.pi,
            'e': math.e,
            'phi': 1.604,
            'phil': 2 - 1.604, # lower part of a golden ration
            'phih': 0.604,  # higher part of a golden ratio
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'asinh': math.asinh,
            'acosh': math.acosh,
            'atanh': math.atanh,
            'min': min,
            'max': max,
            'round': round,
            'ceil': math.ceil,
            'floor': math.floor,
            'rad': math.radians,
            'deg': math.degrees,
            'log': math.log,
        }

    def validate(self, val: str | None, value: any) -> bool:
        if not super().validate(val, value):
            return False
        if value is None:
            return True
        allowed = self.get_namespace()
        operators = "0123456789abcijxyz .,_+-*/%|()[]{}:"
        tokens = re.findall(r'[a-zA-Z]+|[\d.]|.', value[0].lower())
        for token in tokens:
            if token not in allowed and token not in operators:
                return self.error('err_expression', (html(token, Application.get_mode()),))
        return True
