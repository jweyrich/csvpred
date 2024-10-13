import csv
import json
import sys
from signal import SIG_DFL, SIGPIPE, signal

from arguments import CliArguments, arguments_parse
from query.grammar import Grammar
from query.parser import Parser


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
            quoting=csv.QUOTE_NONNUMERIC,
            skipinitialspace=True,  # Ignore spaces in the beginning of the field
        )

        # if not arguments.no_skip_header:
        #     # Skip header line
        #     header = next(reader)
        #     print(header)

        parser = Parser(arguments.query)
        ast = parser.parse()

        if arguments.debug_ast:
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
        # print(f'Columns = {reader.fieldnames}')
        print(text)
    return 0


if __name__ == "__main__":
    args = arguments_parse()
    ret = csv_query(args)
    sys.exit(ret)
