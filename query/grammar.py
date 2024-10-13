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
and_, or_, not_, xor_ = pp.CaselessKeyword.using_each("AND OR NOT XOR".split())
bool_unary_operator = (
    pp.Group(not_)
    .set_results_name("bool_unary_operator")
    .set_parse_action(BoolUnaryOperator.parse)
)
bool_binary_operator = (
    pp.Group(and_ | or_ | xor_)
    .set_results_name("bool_binary_operator")
    .set_parse_action(BoolBinaryOperator.parse)
)
# keyword = and_ | or_ | not_ | xor_

# A number is a sequence of digits, optionally preceded by a minus sign
integer_ = (
    pp.Regex(r"[+-]?\d+")
    .set_name("integer")
    .add_parse_action(lambda tokens: int(tokens[0]))
)
float_ = (
    pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?")
    .set_name("float")
    .add_parse_action(lambda tokens: float(tokens[0]))
)

# Attribute names can contain letters, numbers, underscores, and hyphens
attribute = (
    pp.Word(pp.alphas + "_-", pp.alphanums + "_-")
    .set_results_name("attribute")
    .set_parse_action(Attribute.parse)
)

cmp_operator = (
    pp.one_of(["!=", "==", "<=", ">=", "=", "<", ">"])
    .set_results_name("cmp_operator")
    .set_parse_action(CmpOperator.parse)
)

quoted_string = pp.QuotedString('"')

# How to find the non-alphanum character set? `grep -o . data.csv | sort | uniq -c`
literal_value = (
    # (pp.Word(pp.alphanums + "#&-./:=?_`") | pp.QuotedString('"') | integer_ | float_)
    (pp.Word(pp.alphanums + "-_") | quoted_string | integer_ | float_)
    .set_results_name("literal_value")
    .set_parse_action(LiteralValue.parse)
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
            #     (not_ | "!").set_parse_action(negate_expression_action),
            #     1,
            #     pp.OpAssoc.RIGHT,
            # ),
            (
                (and_ | "&&").set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
            (
                (or_ | "||").set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
            (
                (xor_ | "^").set_parse_action(BoolBinaryOperator.parse),
                2,
                pp.OpAssoc.LEFT,
            ),
            # (and_, 2, pp.OpAssoc.LEFT, lambda tokens: ["and", tokens[0], tokens[2]]),
            # (or_, 2, pp.OpAssoc.LEFT, lambda tokens: ["or", tokens[0], tokens[2]]),
            # (xor_, 2, pp.OpAssoc.LEFT, lambda tokens: ["xor", tokens[0], tokens[2]]),
        ],
    )
    .set_name("grammar")
    .set_parse_action(Grammar.parse)
)
