from __future__ import annotations
"""
Scanner token definitions 
"""

import enum
from typing import Any


TokenType = enum.Enum(
    'Tokens',

    # single char tokens
    ['LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BRACE', 'RIGHT_BRACE',
     'COMMA', 'DOT', 'MINUS', 'PLUS', 'SEMICOLON', 'SLASH', 'STAR',

     # one or two char tokens
     'BANG', 'BANG_EQUAL',
     'EQUAL', 'EQUAL_EQUAL',
     'GREATER', 'GREATER_EQUAL',
     'LESS', 'LESS_EQUAL',

     # Literals.
     'IDENTIFIER', 'STRING', 'NUMBER',

     # Keywords.
     'AND', 'CLASS', 'ELSE', 'FALSE', 'FUN', 'FOR', 'IF', 'NIL', 'OR',
     'PRINT', 'RETURN', 'SUPER', 'THIS', 'TRUE', 'VAR', 'WHILE',

     'EOF'
     ]
)

KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: Any, line: int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    @classmethod
    def mk_token(cls, token_type: TokenType, text: str) -> Token:
        """utility to easily create tokens"""
        return cls(token_type, text, None, 1)

    def __str__(self) -> str:
        # when object is printed
        body = f'{self.token_type}'
        tail = self.literal or self.lexeme
        if tail:
            body = f'{body}[{tail}]'
        return body

    def __repr__(self) -> str:
        # appears in collections
        return self.__str__()
