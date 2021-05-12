from typing import Any, List

from expression import Binary, Expr, Grouping, Literal, Unary
from loxtoken import Token, TokenType
from visitor import Visitor


class AstPrinter(Visitor):
    """
    Visitor for printing AST
    """
    def visit_binary(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *args: List[Expr]) -> str:
        """
        """
        if len(args) == 0:
            return name

        # array of string representations
        str_arr = []
        for subexpr in args:
            subexpr_str = subexpr.accept(self)
            str_arr.append(subexpr_str)

        body = ' '.join(str_arr)
        return f'({name} {body})'

    def print(self, expr: Expr) -> str:
        return expr.accept(self)


if __name__ == '__main__':
    exp0 = Binary(Unary(Token.mk_token(TokenType.MINUS, "-"),
                        Literal(123)),
                  Token.mk_token(TokenType.STAR, "*"),
                  Grouping(Literal(46.32))
                  )
    print(AstPrinter().print(exp0))