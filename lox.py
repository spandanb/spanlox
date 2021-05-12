import sys

from typing import List

from astprinter import AstPrinter
from loxparser import Parser
from interpreter import Interpreter
from reporting import ErrorReporter
from scanner import Scanner


# UTILS


def read_file(filepath: str):
    contents = ''
    with open(filepath, 'r') as fp:
        fp.read()
    return contents


# MAIN LOGIC

class Lox:

    def __init__(self):
        self.error_reporter = ErrorReporter()
        # needed for persisting global variables (not yet supported)
        self.interpreter = Interpreter(self.error_reporter)

    def run(self, source: str):
        """
        run `source` code
        """
        scanner = Scanner(source, self.error_reporter)
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token)
        parser = Parser(tokens, self.error_reporter)
        expression = parser.parse()
        if self.error_reporter.had_error:
            # there was error; lazily exit
            return

        # print(AstPrinter().print(expression))
        self.interpreter.interpret(expression)

    def run_prompt(self):
        """
        run repl prompt
        """
        while True:
            line = input('> ')
            if line == '':
                break
            self.run(line)

    def run_file(self, filepath: str):
        """
        run from file
        """
        source = read_file(filepath)
        self.run(source)
        if self.error_reporter.had_error:
            sys.exit(65)
        if self.error_reporter.had_runtime_error:
            sys.exit(70)

    def main(self):
        """
        run main loop
        """
        # remove script name from args
        args = sys.argv[1:]

        if len(args) > 1:
            print('Usage: spanlox [script]')
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()


if __name__ == '__main__':
    Lox().main()
