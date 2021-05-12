import sys
import os

# be careful, this may causes circular import
from scanner import TokenType


class ErrorReporter:
    """
    handles reporting error
    """

    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def scan_error(self, line: int, message: str):
        """
        Author overloads `error` method for scanning
        and parsing. I will define separate methods.
        """
        self.report(line, "", message)

    def parse_error(self, token, message: str):
        """
        report parsing error
        """
        if token.token_type == TokenType.EOF:
            self.report(token.line, " at end", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: 'LoxRuntimeError'):
        """
        report a runtime error
        """
        output = f'{error.get_message()}{os.linesep}[line {error.token.line}]'
        print(output, file=sys.stderr)
        self.had_runtime_error = False

    def report(self, line: int, where: str, message: str):
        """
        report a non-runtime error
        """
        output = f'[line {line}] Error{where}: {message}'
        print(output, file=sys.stderr)
        self.had_error = True
