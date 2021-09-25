from __future__ import annotations
"""
Definitions for terminal production symbols for the grammar
NOTE: there are two hierarchies- rooted at Stmt and Expr
"""
from dataclasses import dataclass
from typing import Any

from loxtoken import Token

# NOTE: the tutorial uses a utility to generate the
# parser symbol classes; I'm using dataclasses

# TODO: rename this module stmt.py

# NOTE: reconsider the pattern of dataclasses inheriting
# from Stmt or Expr


@dataclass
class Stmt:
    """
    Root of statement hierarchy
    """
    def accept(self, visitor: 'Visitor') -> Any:
        return visitor.visit(self)


@dataclass
class Print(Stmt):
    """
    A print statement
    """
    expression: Expr


@dataclass
class Expression(Stmt):
    """
    An expression statement
    """
    expression: Expr


@dataclass
class Var(Stmt):
    """
    A variable declaration
    """
    name: Token
    initializer: Expr


@dataclass
class Expr:
    """
    This class should not be directly instantiated; but I don't
    want to make it abstract, since I'll need to implement the visit
    methods for each derived (implemented) class.

    TODO: investigate whether I can mark the class abstract
    and still rely on the parent method being callable
    i.e. so each node (implementing) class doesn't have to implement it
    """
    # expression: 'Expr'

    def accept(self, visitor: 'Visitor') -> Any:
        return visitor.visit(self)


@dataclass
class Binary(Expr):
    """
    binary op
    """
    left: Expr
    operator: Token
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
    operator: Token
    right: Expr


@dataclass
class Variable(Expr):
    name: Token
