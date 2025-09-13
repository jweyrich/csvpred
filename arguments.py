"""
This module provides a function to parse command line arguments
"""

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class CliArguments:
    """
    Command line arguments
    """

    input_file: Optional[str] = None
    debug_ast: Optional[bool] = None
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
        required=False,
        dest="input_file",
        help="path to the input CSV file. If not provided, read from stdin",
    )
    parser.add_argument(
        "--debug-ast",
        required=False,
        default=False,
        dest="debug_ast",
        action="store_true",
        help="print the AST (default: %(default)s)",
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
