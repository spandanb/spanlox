"""
Definitions for terminal production symbols for the grammar
"""
from dataclasses import dataclass
from typing import Any

from loxtoken import TokenType

# NOTE: the tutorial uses a utility to generate the
# parser symbol classes; I'm using dataclasses


class Expr:
    """
    abstract class, i.e. should not be instantiated
    but not making `accept` an abstract method, since that would
    require overriding it each subclass.
    """

    def accept(self, visitor: 'Visitor') -> Any:
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


