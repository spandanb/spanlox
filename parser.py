# needed for postponed evaluations, e.g. so types can be forward referenced
from __future__ import annotations

import re

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List

from scanner import TokenType, Token


# NOTE: the tutorial uses a utility to generate the
# parser symbol classes; I'm using dataclasses

# section: utilities
def camel_to_snake(name: str) -> str:
    """
    change casing
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


class ParseException(Exception):
    """
    Generic parse exception
    """
    pass

# section: parser symbol classes


class Expr:
    """
    abstract class, i.e. should not be instantiated
    but not making `accept` an abstract method, since that would
    require overriding it each subclass.
    """

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit(self)


@dataclass
class Binary(Expr):
    """
    binary op
    """
    left: Expr
    operator: TokenType
    right: Expr


@dataclass
class Grouping(Expr):
    """
    a grouping, i.e. via bracketing
    """
    expression: Expr


@dataclass
class Literal(Expr):
    """
    literal
    """
    value: Any


@dataclass
class Unary(Expr):
    """
    unary op
    """
    operator: TokenType
    right: Expr


# section : other logic

class Visitor(ABC):
    """
    Conceptually, Visitor is an interface/abstract class,
    where different concrete Visitors, e.g. AstPrinter can handle
    different tasks, e.g. printing tree, evaluating tree.
    This indirection allows us to add new behaviors for the parser
    via a new concrete class; instead of either: 1) modifying
    the parser symbol classes (OOF), or 2) adding a new function
    for any new behavior (e.g. functional)

    See following for visitor design pattern in python:
     https://refactoring.guru/design-patterns/visitor/python/example
    """
    pass

    @abstractmethod
    def visit(self, expr: Expr):
        """
        this will determine which specific handler to invoke

        NOTE: The tutorial defines separate methods for each
        expr type. But that's partly because of java, where reflection
        is awkward at best. In python, defining each method seems
        very manual, with no real gain in type safety, unlike java.
        More broadly, I'll use python dynamism, unless some substantial
        gain in readability or expressability is needed
        """
        pass


class AstPrinter(Visitor):
    """
    Visitor for printing AST
    """

    def visit(self, expr: Expr) -> Any:
        """
        visit method; determines which specific
        helper method to call
        """
        suffix = camel_to_snake(expr.__class__.__name__)
        # determine the name of the handler method from class of expr
        # NB: this requires the class and handler have the
        # same name in PascalCase and snake_case, respectively
        handler = f'visit_{suffix}'
        if hasattr(self, handler):
            return getattr(self, handler)(expr)
        else:
            print(f"astprinter does not have {handler}")
            raise ParseException()

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
    expr = Binary(Unary(Token.mk_token(TokenType.MINUS, "-"),
                        Literal(123)),
                  Token.mk_token(TokenType.STAR, "*"),
                  Grouping(Literal(46.32))
                  )
    print(AstPrinter().print(expr))