import sys


class ErrorReporter:
    """
    handles reporting error
    """

    def __init__(self):
        self.had_error = False

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        output = f'[line {line}] Error{where}: {message}'
        print(output, file=sys.stderr)
        self.had_error = True
