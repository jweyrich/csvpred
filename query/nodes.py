from abc import ABC, abstractmethod
from typing import Self

import pyparsing as pp

from .exec import exec_bool_binary_operator, exec_bool_unary_operator, exec_cmp_operator


class Node(ABC):
    """
    Base class for all nodes in the AST.
    """

    def __init__(self, children):
        self.children = children

    @abstractmethod
    def evaluate(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.children)


class Grammar(Node):
    """
    The top-level grammar node.
    """

    def __init__(self, exprs):
        super().__init__([exprs])
        self.expressions = exprs

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        if isinstance(self.expressions, Expression):
            return self.expressions.evaluate(row)
        else:
            raise ValueError(f"Unknown grammar {type(self)} {self}")

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        exprs = value
        return Grammar(exprs=exprs)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.expressions)


class Expression(Node):
    def __init__(self, exprs):
        super().__init__([exprs])
        self.expressions = exprs

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        if isinstance(self.expressions, Expression):
            return self.expressions.evaluate(row)
        elif isinstance(self.expressions, NegateExpression):
            return self.expressions.evaluate(row)
        elif isinstance(self.expressions, BinaryExpression):
            return self.expressions.evaluate(row)
        elif isinstance(self.expressions, Comparison):
            return self.expressions.evaluate(row)
        elif isinstance(self.expressions, Identifier):
            return self.expressions.evaluate(row)
        else:
            raise ValueError(f"Unknown expression {type(self)} {self}")

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        exprs = value
        return Expression(exprs=exprs)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.expressions)


class Identifier(Node):
    def __init__(self, value):
        super().__init__([value])
        self.value = value

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        if isinstance(self.value, Attribute):
            return self.value.evaluate(row)
        else:
            raise ValueError(f"Unknown identifier {type(self)} {self}")

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        value = value[0]
        return Identifier(value=value)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)


class Comparison(Node):
    def __init__(self, ident, oper, value):
        super().__init__([ident, oper, value])
        self.identifier = ident
        self.operator = oper
        self.value = value

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        left = self.identifier.evaluate(row)
        operator = self.operator.evaluate()
        right = self.value.evaluate()

        return exec_cmp_operator(operator, left, right)

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        ident = value[0]
        oper = value[1]
        value = value[2]
        return Comparison(ident=ident, oper=oper, value=value)

    def __repr__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__,
            self.identifier,
            self.operator,
            self.value,
        )


class CmpOperator(Node):
    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        operator = value
        return CmpOperator(operator=operator)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.operator)


class BoolUnaryOperator(Node):
    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        operator = value[0]
        return BoolUnaryOperator(operator=operator)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.operator)


class NegateExpression(Node):
    def __init__(self, expr):
        super().__init__([expr])
        self.expression = expr

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        right = self.expression.evaluate(row)
        return exec_bool_unary_operator("not", right)

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        operator = value[0]
        if (
            not isinstance(operator, BoolUnaryOperator)
            or not (operator.operator == "NOT" or operator.operator == "!")
        ):
            raise ValueError(
                f"Expected a BoolUnaryOperator, got {type(operator)} {operator}"
            )
        expr = value[1]
        return NegateExpression(expr=expr)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.expression)


class BinaryExpression(Node):
    def __init__(self, left, operator, right):
        super().__init__([left, operator, right])
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        left = self.left.evaluate(row)
        operator = self.operator.evaluate()
        right = self.right.evaluate(row)

        return exec_bool_binary_operator(operator, left, right)

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        left = value[0]
        operator = value[1]
        right = value[2]
        return BinaryExpression(left=left, operator=operator, right=right)

    def __repr__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__,
            self.left,
            self.operator,
            self.right,
        )


class BoolBinaryOperator(Node):
    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        operator = value[0]
        return BoolBinaryOperator(operator=operator)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.operator)


class LiteralValue(Node):
    def __init__(self, value):
        super().__init__([value])
        self.value = value

    def evaluate(self):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.value

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        return LiteralValue(value=value)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.value)


class Attribute(Node):
    def __init__(self, name):
        super().__init__([name])
        self.name = name

    def evaluate(self, row):
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return row[self.name]

    @staticmethod
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        # print("%s.parse: %s" % (self.__class__.__name__, repr(tokens)))
        value = tokens[0]
        name = value
        return Attribute(name=name)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.name)
