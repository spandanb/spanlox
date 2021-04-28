import sys

from typing import List

from astprinter import AstPrinter
from loxparser import Parser
from reporting import ErrorReporter
from scanner import Scanner


# UTILS


def read_file(filepath: str):
    contents = ''
    with open(filepath, 'r') as fp:
        fp.read()
    return contents


# MAIN LOGIC


def run(source: str):
    """
    run some source code
    """
    error_reporter = ErrorReporter()
    scanner = Scanner(source, error_reporter)
    tokens = scanner.scan_tokens()
    for token in tokens:
        print(token)
    parser = Parser(tokens, error_reporter)
    expression = parser.parse()
    if error_reporter.had_error:
        # there was error; lazily exit
        return

    print(AstPrinter().print(expression))


def run_prompt():
    while True:
        line = input('> ')
        if line == '':
            break
        run(line)


def run_file(filepath: str):
    source = read_file(filepath)
    run(source)


def main():
    """
    run main loop
    """
    # remove script name from args
    args = sys.argv[1:]

    if len(args) > 1:
        print('Usage: spanlox [script]')
        sys.exit(64)
    elif len(args) == 1:
        run_file(args[0])
    else:
        run_prompt()


if __name__ == '__main__':
    main()
