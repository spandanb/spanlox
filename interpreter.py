from numbers import Number
from typing import Any

from loxtoken import TokenType, Token
from expression import Binary, Expr, Grouping, Literal, Unary
from visitor import Visitor, HandlerNotFoundException


class InterpretationError(Exception):
    pass


class LoxRuntimeError(Exception):
    def __init__(self, operator: Token, message: str):
        super().__init__(message)
        self.operator = operator

    def get_message(self):
        return self.args[0]


class Interpreter(Visitor):
    """
    Visitor for interpreting/executing AST
    """
    def __init__(self, error_reporter: 'ErrorReporter'):
        self.error_reporter = error_reporter

    def interpret(self, expr: Expr):
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except LoxRuntimeError as e:
            self.error_reporter.runtime_error(e)

    def evaluate(self, expr: Expr):
        """
        evaluate expression
        """
        return expr.accept(self)

    @staticmethod
    def stringify(obj) -> str:
        if obj is None:
            return 'nil'
        # NOTE: author uses double as the underlying type and thus needs
        # to do string manipulation to display integer valued doubles as ints- i.e. truncating '.0';
        # I'm relying on Python's handling of numeric types (integer and float),
        # and so don't explicitly handle the type as a float, and hence don't
        # need to do string manipulation
        return str(obj)

    def visit_literal(self, expr: Literal) -> Any:
        return expr.value

    def visit_grouping(self, expr: Grouping) -> Any:
        self.evaluate(expr.expression)

    def visit_unary(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.operator == TokenType.BANG:
            return self.is_truthy(right)
        elif expr.operator == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -1 * float(right);

        return None

    def visit_binary(self, expr: Binary) -> Any:
        """
        evaluate binary expression
        NB: this evaluates operands from left-to-right order
        """

        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.token_type == TokenType.MINUS:
            return left - right
        elif expr.operator.token_type == TokenType.SLASH:
            return left / right
        elif expr.operator.token_type == TokenType.STAR:
            return left * right
        elif expr.operator.token_type == TokenType.PLUS:
            # overloaded to support both number and string operands
            # NB: not casting to double; the underlying type could be an int or float
            if isinstance(left, Number) and isinstance(right, Number):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                raise InterpretationError("mismatched types")
        elif expr.operator.token_type == TokenType.GREATER:
            return left > right
        elif expr.operator.token_type == TokenType.GREATER_EQUAL:
            return left >= right
        elif expr.operator.token_type == TokenType.LESS:
            return left < right
        elif expr.operator.token_type == TokenType.LESS_EQUAL:
            return left <= right
        elif expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        # unreachable
        return None

    @staticmethod
    def is_truthy(obj) -> bool:
        """
        determine whether obj is truthy
        Using Ruby lang's falsy criteria:
        None and False are false; rest are truthy
        """
        if obj is None:
            return False
        elif isinstance(obj, bool):
            return obj
        return True

    @staticmethod
    def check_number_operand(operator: Token, right: Any):
        if not isinstance(right, Number):
            raise LoxRuntimeError(operator, "Operand must be a number")

    @staticmethod
    def is_equal(a, b) -> bool:
        """
        NB: a and b can be arbitrary types
        python is smart enough to handle this
        """
        return a == b
