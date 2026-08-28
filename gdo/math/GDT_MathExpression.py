import ast
import math
import re

from gdo.base.Application import Application
from gdo.base.Util import html
from gdo.core.GDT_RestOfText import GDT_RestOfText


class GDT_MathExpression(GDT_RestOfText):
    """
    A math expression to evaluate.
    """

    MAX_LENGTH = 256
    MAX_NODES = 128
    MAX_POWER = 128

    def get_namespace(self) -> dict:
        return {
            'for': 'for',
            'in': 'in',
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

    def validate(self, val: str | None) -> bool:
        if not super().validate(val):
            return False
        if val is None:
            return True

        # eval() is kept for the small, math-only namespace below. Validate
        # the actual syntax tree as well: 10**10**10 must not monopolise a
        # Dog worker.
        if len(val) > self.MAX_LENGTH:
            return self.error('err_expression', ('Expression too long',))

        try:
            tree = ast.parse(val, mode='eval')
        except SyntaxError:
            return self.error('err_expression', ('Invalid syntax',))

        if sum(1 for _ in ast.walk(tree)) > self.MAX_NODES:
            return self.error('err_expression', ('Expression too complex',))

        allowed = self.get_namespace()
        operators = "0123456789abcijxyz .,_+-*/%|()[]{}:"
        tokens = re.findall(r'[a-z]+|[\d.]|.', val.lower())
        for token in tokens:
            if token not in allowed and token not in operators:
                return self.error('err_expression', (html(token, Application.get_mode()),))

        allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.BitOr)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Expression, ast.Load, ast.operator, ast.unaryop)):
                continue
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                    continue
                return self.error('err_expression', ('Only numeric values are allowed',))
            if isinstance(node, ast.Name):
                if node.id in allowed and node.id not in ('for', 'in'):
                    continue
                return self.error('err_expression', (html(node.id, Application.get_mode()),))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                continue
            if isinstance(node, ast.BinOp) and isinstance(node.op, allowed_ops):
                if isinstance(node.op, ast.Pow):
                    if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, int) or not 0 <= node.right.value <= self.MAX_POWER:
                        return self.error('err_expression', ('Power exponents must be integers from 0 to 128',))
                continue
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and callable(allowed.get(node.func.id)) and not node.keywords:
                    continue
                return self.error('err_expression', ('Only approved math functions are allowed',))
            if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
                continue
            return self.error('err_expression', ('Unsupported expression',))

        return True
