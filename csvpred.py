import argparse
import csv
import json
import sys
from dataclasses import dataclass
from signal import SIG_DFL, SIGPIPE, signal
from typing import Optional

from query.grammar import Grammar
from query.parser import Parser


@dataclass
class CliArguments:
    """
    Command line arguments
    """

    input_file: Optional[str] = None
    encoding: Optional[str] = None
    fieldnames: Optional[str] = None
    no_skip_header: Optional[bool] = None
    query: Optional[str] = None


def arguments_parse() -> CliArguments:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Find a role in the CSV file")
    parser.add_argument(
        "-i",
        "--input-file",
        required=True,
        dest="input_file",
        help="path to the input CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        required=False,
        default="utf-8",
        dest="encoding",
        help="encoding of the input CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "-f",
        "--fieldnames",
        required=False,
        dest="fieldnames",
        help="specify alternative column names separated by commas (example: col1,col2,col3)",
    )
    parser.add_argument(
        "-n",
        "--no-skip-header",
        required=False,
        default=False,
        dest="no_skip_header",
        action="store_true",
        help="do not skip the header line (default: %(default)s)",
    )
    parser.add_argument(
        "-q",
        "--query",
        required=True,
        dest="query",
        help="query predicate to be applied to the CSV file",
    )
    parsed_args = parser.parse_args()
    args_dict = vars(parsed_args)
    return CliArguments(**args_dict)


def csv_query(arguments: CliArguments) -> int:
    """
    Run a filter on the CSV file and output the matching rows
    """
    # Ignore SIGPIPE signal when the output is piped to another command
    signal(SIGPIPE, SIG_DFL)

    with open(arguments.input_file, newline="", encoding=arguments.encoding) as csvfile:
        fieldnames = arguments.fieldnames.split(",") if arguments.fieldnames else None
        reader = csv.DictReader(
            csvfile,
            fieldnames=fieldnames,
            delimiter=",",
            quotechar='"',
            skipinitialspace=True,  # Ignore spaces in the beginning of the field
        )

        # if not arguments.no_skip_header:
        #     # Skip header line
        #     header = next(reader)
        #     print(header)

        parser = Parser(arguments.query)
        ast = parser.parse()
        parser.dump_ast(ast)

        def make_filter(ast):
            def run_filter(row) -> bool:
                grammar = ast[0]
                if not isinstance(grammar, Grammar):
                    raise ValueError(f"Unknown grammar {grammar}")
                result = grammar.evaluate(row)
                return result

            return run_filter

        results = []
        filter_fn = make_filter(ast)
        results = filter(filter_fn, reader)

        text = json.dumps(list(results))
        print("#" * 120)
        # print(f'Columns = {reader.fieldnames}')
        print(text)
        print("#" * 120)
    return 0


if __name__ == "__main__":
    args = arguments_parse()
    ret = csv_query(args)
    sys.exit(ret)
