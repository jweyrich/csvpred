import sys

import pyparsing as pp

from .grammar import grammar
from .nodes import Node


class ParserException(Exception):
    """
    Exception raised when a parser error occurs.
    """
    def __init__(self, message: str, cause: pp.ParseException):
        super().__init__(message)
        self.row = cause.lineno
        self.column = cause.col
        self.mark_input_line = cause.markInputline()


class Parser(object):
    """
    Parser class for the query language.
    """

    def __init__(self, value=None):
        self.original_input = value
        self._parse_results = None

    def parse(self) -> pp.ParseResults:
        """
        Parse the input string and return the parse results.
        """
        try:
            parse_results = grammar.parse_string(self.original_input, parse_all=True)
        except pp.ParseException as e:
            message = f"Query syntax error at line {e.lineno} col {e.col}"
            raise ParserException(message=message, cause=e) from e
        else:
            self._parse_results = parse_results
            return self._parse_results

    def dump_ast(self, node: Node):
        """
        Dump the AST to the console.
        """
        print(f"AST repr:\n{node}", file=sys.stderr)
        print("AST tree:", file=sys.stderr)
        self._dump_ast_node_recursively(node)

    def _dump_ast_node_recursively(self, node, tab=""):
        """
        Recursively dump the AST nodes to the console.
        """
        text = f"('{node}')" if isinstance(node, str | float | int) else ""
        print(tab + "┗━ " + str(node.__class__.__name__) + text, file=sys.stderr)
        if isinstance(node, Node):
            for child in node.children:
                self._dump_ast_node_recursively(child, tab + "   ")
        elif isinstance(node, pp.ParseResults):
            for child in node:
                self._dump_ast_node_recursively(child, tab + "   ")
        elif isinstance(node, list):
            for child in node:
                self._dump_ast_node_recursively(child, tab + "   ")
