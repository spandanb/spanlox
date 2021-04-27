# needed for postponed evaluations, e.g. so types can be forward referenced
from __future__ import annotations

import re

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List

from scanner import TokenType, Token
from reporting import ErrorReporter


# NOTE: the tutorial uses a utility to generate the
# parser symbol classes; I'm using dataclasses

# section: utilities

def camel_to_snake(name: str) -> str:
    """
    change casing
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# section: Exception/Error classes

class ParseError(Exception):
    """
    """


class ParserHandlerNotException(Exception):
    """
    A specific handler (method) is not found;
    defined by me
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


# section : visitors

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
            print(f"AstPrinter does not have {handler}")
            raise ParserHandlerNotException()

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


# section : parser

class Parser:
    """
    parser

    grammar used:
    expression     → equality ;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           → factor ( ( "-" | "+" ) factor )* ;
    factor         → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary
                   | primary ;
    primary        → NUMBER | STRING | "true" | "false" | "nil"
                   | "(" expression ")" ;
    """
    def __init__(self, tokens: List[Token], error_reporter):
        self.tokens = tokens
        self.current = 0  # points to token to parse
        self.error_reporter = error_reporter

    def expression(self) -> Expr:
        """
        expression     → equality ;
        """
        return self.equality()

    def equality(self) -> Expr:
        """
        equality       → comparison ( ( "!=" | "==" ) comparison )* ;
        """
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        """
        comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
        """
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        """
        term  → factor ( ( "-" | "+" ) factor )* ;
        """
        expr = self.factor()
        # minus, then plus, due to order of precedence
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        """
        factor         → unary ( ( "/" | "*" ) unary )* ;
        """
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        """
        unary          → ( "!" | "-" ) unary
                      | primary ;
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        """
        primary     → NUMBER | STRING | "true" | "false" | "nil"
                    | "(" expression ")" ;
        """
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        else:
            raise self.error(self.peek(), "Expect expression.")

    # section : helper methods

    def match(self, *types: List[TokenType]) -> bool:
        """
        if any of `types` match the current type consume and return True
        """
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType):
        """
        return True if `token_type` matches current token
        """
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        """
        consumes current token(i.e. increments
        current pointer) and returns it
        """
        if self.is_at_end() is False:
            self.current += 1
        return self.previous()

    def consume(self, token_type: TokenType, message: str) -> Token:
        """
        check whether next token matches expectation; otherwise
        raises exception
        """
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def error(self, token, message: str) -> ParseError:
        """
        report error and return error sentinel object
        """
        self.error_reporter.parse_error(token, message)
        return ParseError()

    def synchronize(self):
        """
        synchronizes state of parser on error
        """
        self.advance()
        while self.is_at_end() is False:
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF,
                                          TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return
            self.advance()

    def parse(self):
        """
        main entry point to parser
        """
        try:
            return self.expression()
        except ParseError:
            return None


if __name__ == '__main__':
    exp0 = Binary(Unary(Token.mk_token(TokenType.MINUS, "-"),
                        Literal(123)),
                  Token.mk_token(TokenType.STAR, "*"),
                  Grouping(Literal(46.32))
                  )
    print(AstPrinter().print(exp0))