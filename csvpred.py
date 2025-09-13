"""
This is the main module for the csvpred command line tool.
"""

import csv
import json
import sys
from signal import SIG_DFL, SIGPIPE, signal
from typing import TextIO

from arguments import CliArguments, arguments_parse
from query.grammar import Grammar
from query.parser import Parser, ParserException


def make_filter(grammar: Grammar):
    """
    Create a filter function to filter each row
    """
    if not isinstance(grammar, Grammar):
        raise ValueError(f"Unknown grammar {grammar}")

    def run_filter(row) -> bool:
        result = grammar.evaluate(row)
        return result

    return run_filter


def open_file(file_path: str | None, encoding: str | None) -> TextIO:
    """
    Open the file for reading.
    If the file_path is None or "stdin", return sys.stdin
    """
    if not file_path or file_path == "stdin":
        return sys.stdin
    try:
        return open(file_path, newline="", encoding=encoding)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def csv_query(arguments: CliArguments) -> int:
    """
    Run a filter on the CSV file and output the matching rows
    """
    # Ignore SIGPIPE signal when the output is piped to another command
    signal(SIGPIPE, SIG_DFL)

    parser = Parser(arguments.query)
    try:
        grammar = parser.parse()
    except ParserException as e:
        error_message = e.args[0]
        print(error_message, file=sys.stderr)
        print(f"> {arguments.query}", file=sys.stderr)
        print(" " * (e.column - 1 + len("> ")) + "^", file=sys.stderr)
        return 1

    if arguments.debug_ast:
        parser.dump_ast(grammar)

    fieldnames = arguments.fieldnames.split(",") if arguments.fieldnames else None

    with open_file(arguments.input_file, encoding=arguments.encoding) as csvfile:
        reader = csv.DictReader(
            csvfile,
            fieldnames=fieldnames,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC,
            skipinitialspace=True,  # Ignore spaces in the beginning of the field
        )

        if not arguments.no_skip_header:
            # Skip header line
            next(reader)

        filter_fn = make_filter(grammar)
        results = list(filter(filter_fn, reader))
        output = json.dumps(results)
        print(output)
    return 0


if __name__ == "__main__":
    args = arguments_parse()
    ret = csv_query(args)
    sys.exit(ret)
