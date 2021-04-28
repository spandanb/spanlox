# needed for postponed evaluations, e.g. so types can be forward referenced
from __future__ import annotations

from typing import Any, List

from expression import Binary, Expr, Grouping, Literal, Unary
from loxtoken import TokenType, Token


class ParseError(Exception):
    """
    """


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
    def __init__(self, tokens: List[Token], error_reporter: 'ErrorReporter'):
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

