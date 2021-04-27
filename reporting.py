import sys

# be careful, this may causes circular import
from scanner import TokenType


class ErrorReporter:
    """
    handles reporting error
    """

    def __init__(self):
        self.had_error = False

    def scan_error(self, line: int, message: str):
        """
        Author overloads `error` method for scanning
        and parsing. I will define separate methods.
        """
        self.report(line, "", message)

    def parse_error(self, token, message: str):
        """
        """
        if token.token_type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def report(self, line: int, where: str, message: str):
        output = f'[line {line}] Error{where}: {message}'
        print(output, file=sys.stderr)
        self.had_error = True
