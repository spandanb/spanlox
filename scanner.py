from __future__ import annotations

from typing import List, Any

from loxtoken import TokenType, Token, KEYWORDS


class Scanner:
    def __init__(self, source: str, error_reporter: 'ErrorReporter'):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1
        self.error_reporter = error_reporter

    def is_at_end(self) -> bool:
        """return true if scanner is at end of the source"""
        return self.current >= len(self.source)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def match(self, expected: str):
        """
        conditionally increment current ptr, if current
        char matches expected
        """
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        # conditionally increment on match
        self.current += 1
        return True

    def peek(self) -> str:
        """
        return next character, without consuming it
        """
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """
        returns next to next lookahead character
        """
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def scan_tokens(self) -> List[Token]:
        """
        scan source and return list of scanned tokens
        """
        while self.is_at_end() is False:
            self.start = self.current
            self.scan_token()

        self.add_token(TokenType.EOF, 'EOF')
        return self.tokens

    def add_token(self, token_type: TokenType, literal: Any = None):
        text = self.source[self.start: self.current]
        new_token = Token(token_type, text, literal, self.line)
        self.tokens.append(new_token)

    def tokenize_string(self):
        """
        tokenize string
        """
        while self.peek() != '"' and self.is_at_end() is False:
            if self.peek() == '\n':  # supports multiline strings
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error_reporter.scan_error(self.line, f'Unterminated string')

        # the closing "
        self.advance()
        # trim enclosing quotation marks
        value = self.source[self.start+1: self.current-1]
        self.add_token(TokenType.STRING, value)

    def tokenize_number(self):
        """
        tokenize a number i.e. an integer or floating point
        """
        # whole-number part
        while self.peek().isdigit():
            self.advance()

        # fractional part
        if self.peek() == '.' and self.peek_next().isdigit():
            # consume the "."
            self.advance()

            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start: self.current])
        self.add_token(TokenType.NUMBER, value)

    def tokenize_identifier(self):
        """
        tokenize identifier using maximum mulch. First check if identifier
        is a keyword. If so, add keyword token. Otherwise,
        add as identifier.
        """
        while self.peek().isalnum():
            self.advance()
        identifier = self.source[self.start: self.current]
        if identifier in KEYWORDS:
            # reserved keyword
            token_type = KEYWORDS[identifier]
            self.add_token(token_type)
        else:
            # identifier
            self.add_token(TokenType.IDENTIFIER)

    def scan_token(self):
        """

        """
        char = self.advance()
        if char == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif char == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ',':
            self.add_token(TokenType.COMMA)
        elif char == '.':
            self.add_token(TokenType.DOT)
        elif char == '-':
            self.add_token(TokenType.MINUS)
        elif char == '+':
            self.add_token(TokenType.PLUS)
        elif char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif char == '*':
            self.add_token(TokenType.STAR)
        # for these look at second char
        elif char == '!':
            token_type = TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG
            self.add_token(token_type)
        elif char == '=':
            token_type = TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL
            self.add_token(token_type)
        elif char == '<':
            token_type = TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS
            self.add_token(token_type)
        elif char == '>':
            token_type = TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER
            self.add_token(token_type)
        elif char == '/':
            if self.match('/'):
                # comment goes to the end of the line
                while self.peek() != '\n' and self.is_at_end() is False:
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif char == ' ' or char == '\r' or char == '\t':
            # ignore whitespace
            pass
        elif char == '\n':
            self.line += 1
        elif char == '"':  # handle string literal
            self.tokenize_string()
        elif char.isdigit():  # handle numeric literal
            self.tokenize_number()
        elif char.isidentifier():
            self.tokenize_identifier()
        else:
            self.error_reporter.scan_error(self.line, f'Unexpected character [{char}]')


if __name__ == '__main__':
    from reporting import ErrorReporter

    src = 'x = "meow"'
    scanner = Scanner(src, ErrorReporter())
    tokens = scanner.scan_tokens()
    print(tokens)