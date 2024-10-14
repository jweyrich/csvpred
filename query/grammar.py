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

#
# Define the PEG for the filter predicate
#

lparen = pp.Suppress("(")
rparen = pp.Suppress(")")

# Bool operators
and_, and_symbol, or_, or_symbol, not_, not_symbol, xor_, xor_symbol = (
    pp.CaselessKeyword.using_each("AND && OR || NOT ! XOR ^".split())
)

bool_unary_operator = (
    pp.Group(not_ | not_symbol)
    .set_results_name("bool_unary_operator")
    .set_parse_action(BoolUnaryOperator.parse)
)

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

quoted_string = pp.QuotedString('"')

# An unquoted string starts with a letter or underscore, followed by
# 0 or more letters, digits, or underscores
unquoted_string = pp.Word(pp.alphas + "_", pp.alphanums + "_")

literal_string = (
    (quoted_string | unquoted_string)
    .set_results_name("literal_string")
    .set_parse_action(lambda tokens: tokens[0])
)

# How to find the non-alphanum character set? `grep -o . data.csv | sort | uniq -c`
literal_value = (
    (literal_float | literal_integer | literal_string)
    .set_results_name("literal_value")
    .set_parse_action(LiteralValue.parse)
)

# Attribute starts with a dot followed by a sequence of letters, digits, underscores, dashes
attribute = (
    pp.Group(pp.Suppress(".") + literal_string)
    .set_results_name("attribute")
    .set_parse_action(Attribute.parse)
)

identifier = (
    pp.Group(attribute).set_name("identifier").set_parse_action(Identifier.parse)
)

# A comparison has an identifier, an operator, and a value
comparison = (
    pp.Group(identifier + cmp_operator + literal_value)
    .set_results_name("comparison")
    .set_parse_action(Comparison.parse)
)

negate_expression = pp.Forward()
binary_expression = pp.Forward()

expression = pp.Forward().set_name("expression")
expression <<= (
    # ~not_
    # # + pp.Opt(and_condition + pp.ZeroOrMore(or_ + and_condition))
    # + pp.Opt(pp.Group(condition + bool_binary_operator + condition))
    # + pp.Opt(condition)
    pp.Opt(binary_expression)
    + pp.Opt(negate_expression)
    + pp.Opt(comparison)
    + pp.Opt(lparen + expression + rparen)
    + pp.Opt(identifier)
    + pp.Opt(attribute)
    + pp.Opt(literal_value)
).set_parse_action(Expression.parse)

negate_expression <<= (
    pp.Group(bool_unary_operator + expression)
    .set_results_name("negate_expression")
    .set_parse_action(NegateExpression.parse)
)

binary_expression <<= (
    # FIXME(jweyrich): Figure out how to make this work with `expression`s instead of `comparison`s.
    pp.Group(comparison + bool_binary_operator + comparison)
    .set_results_name("binary_expression")
    .set_parse_action(BinaryExpression.parse)
)

grammar = pp.Forward()
grammar <<= (
    pp.infix_notation(
        expression,
        [
            # (
            #     (not_ | not_symbol).set_parse_action(NegateExpression.parse),
            #     1,
            #     pp.OpAssoc.RIGHT,
            #     lambda tokens: ["not", tokens]
            # ),
            (
                (and_ | and_symbol).set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
            (
                (or_ | or_symbol).set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
            (
                (xor_ | xor_symbol).set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
        ],
    )
    .set_name("grammar")
    .set_parse_action(Grammar.parse)
)
