"""
This module defines the grammar for the filter predicate.
"""

import pyparsing as pp

from .nodes import (
    Attribute,
    BinaryExpression,
    BoolBinaryOperator,
    BoolUnaryOperator,
    CmpOperator,
    Comparison,
    Expression,
    Grammar,
    Identifier,
    LiteralValue,
    NegateExpression,
)

lparen = pp.Suppress("(")
rparen = pp.Suppress(")")

# Define the boolean operators
and_, and_symbol, or_, or_symbol, not_, not_symbol, xor_, xor_symbol = (
    pp.CaselessKeyword.using_each("AND && OR || NOT ! XOR ^".split())
)

# Define the unary operators
bool_unary_operator = (
    pp.Group(not_ | not_symbol)
    .set_results_name("bool_unary_operator")
    .set_parse_action(BoolUnaryOperator.parse)
)

# Define the binary operators
bool_binary_operator = (
    pp.Group(and_ | and_symbol | or_ | or_symbol | xor_ | xor_symbol)
    .set_results_name("bool_binary_operator")
    .set_parse_action(BoolBinaryOperator.parse)
)

# keyword = and_ | and_symbol | or_ | or_symbol | not_ | not_symbol | xor_ | xor_symbol

# A number is a sequence of digits, optionally preceded by a minus sign
literal_integer = (
    pp.Regex(r"[+-]?\d+")
    .set_name("integer")
    .add_parse_action(lambda tokens: int(tokens[0]))
)

literal_float = (
    pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?")
    .set_name("float")
    .add_parse_action(lambda tokens: float(tokens[0]))
)

cmp_operator = (
    pp.one_of(["!=", "==", "<=", ">=", "<", ">"])
    .set_results_name("cmp_operator")
    .set_parse_action(CmpOperator.parse)
)

quoted_string = pp.QuotedString('"') | pp.QuotedString("'")

# An unquoted string starts with a letter or underscore, followed by
# 0 or more letters, digits, or underscores
unquoted_string = pp.Word(pp.alphas + "_", pp.alphanums + "_")

literal_string = (
    (quoted_string | unquoted_string)
    .set_results_name("literal_string")
    .set_parse_action(lambda tokens: tokens[0])
)

# A literal value is either a float, an integer, or a string
literal_value = (
    (literal_float | literal_integer | literal_string)
    .set_results_name("literal_value")
    .set_parse_action(LiteralValue.parse)
)

# An attribute starts with a dot followed by a literal string
attribute = (
    pp.Group(pp.Suppress(".") + literal_string)
    .set_results_name("attribute")
    .set_parse_action(Attribute.parse)
)

# An identifier is an attribute
identifier = (
    pp.Group(attribute).set_name("identifier").set_parse_action(Identifier.parse)
)

# A comparison is a sequence of an identifier, a comparison operator, and a literal value
comparison = (
    pp.Group(identifier + cmp_operator + literal_value)
    .set_results_name("comparison")
    .set_parse_action(Comparison.parse)
)

base_expression = comparison

grammar = (
    pp.infix_notation(
        base_expression,
        [
            (
                (not_ | not_symbol),
                1,
                pp.OpAssoc.RIGHT,
                lambda tokens: NegateExpression(Expression(tokens[0][1]))
            ),
            (
                (and_ | and_symbol),
                2,
                pp.OpAssoc.LEFT,
                lambda tokens: BinaryExpression(
                    Expression(tokens[0][0]),
                    BoolBinaryOperator("AND"),
                    Expression(tokens[0][2])
                )
            ),
            (
                (or_ | or_symbol),
                2,
                pp.OpAssoc.LEFT,
                lambda tokens: BinaryExpression(
                    Expression(tokens[0][0]),
                    BoolBinaryOperator("OR"),
                    Expression(tokens[0][2])
                )
            ),
            (
                (xor_ | xor_symbol),
                2,
                pp.OpAssoc.LEFT,
                lambda tokens: BinaryExpression(
                    Expression(tokens[0][0]),
                    BoolBinaryOperator("XOR"),
                    Expression(tokens[0][2])
                )
            ),
        ],
    )
    .set_name("grammar")
    .set_parse_action(lambda tokens: Grammar(Expression(tokens[0])))
)
