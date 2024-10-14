"""
This module contains the classes for the nodes in the AST.
"""

import sys
from abc import ABC, abstractmethod
from typing import Self

import pyparsing as pp


class ASTNode(ABC):
    """
    Base class for all nodes in the AST.
    """

    def __init__(self, children):
        self.children = children

    @abstractmethod
    def evaluate(self):
        """
        Evaluate the node.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.children})"


class Grammar(ASTNode):
    """
    Represents the top-level grammar node in the AST.
    """

    def __init__(self, exprs):
        super().__init__([exprs])
        self.expressions = exprs

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the grammar.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        if isinstance(self.expressions, Expression):
            return self.expressions.evaluate(row)
        else:
            raise ValueError(f"Unknown grammar {type(self)} {self}")

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the grammar.
        """
        # print(f"{Grammar.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        exprs = value
        return Grammar(exprs=exprs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expressions})"


class Expression(ASTNode):
    """
    Represents an expression node in the AST.
    """

    def __init__(self, exprs):
        super().__init__([exprs])
        self.expressions = exprs

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the expression.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        accepted_types = (
            Expression | NegateExpression | BinaryExpression | Comparison | Identifier
        )
        # This requires Python >= 3.10 (PEP 604)
        if isinstance(self.expressions, accepted_types):
            return self.expressions.evaluate(row)
        else:
            raise ValueError(f"Unknown expression {type(self)} {self}")

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the expression.
        """
        # print(f"{Expression.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        exprs = value
        return Expression(exprs=exprs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expressions})"


class Identifier(ASTNode):
    """
    Represents an identifier node in the AST.
    """

    def __init__(self, value):
        super().__init__([value])
        self.value = value

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the identifier.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        if isinstance(self.value, Attribute):
            return self.value.evaluate(row)
        else:
            raise ValueError(f"Unknown identifier {type(self)} {self}")

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the identifier.
        """
        # print(f"{Identifier.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        value = value[0]
        return Identifier(value=value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class Comparison(ASTNode):
    """
    Represents a comparison node in the AST.
    """

    def __init__(self, ident, oper, value):
        super().__init__([ident, oper, value])
        self.identifier = ident
        self.operator = oper
        self.value = value

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the comparison.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        left = self.identifier.evaluate(row)
        operator = self.operator.evaluate()
        right = self.value.evaluate()
        return self.apply(operator, left, right)

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the comparison.
        """
        # print(f"{Comparison.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        ident = value[0]
        oper = value[1]
        value = value[2]
        return Comparison(ident=ident, oper=oper, value=value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.identifier}, {self.operator}, {self.value})"

    def apply(self, operator, left, right):
        """
        Apply a comparison operator.
        """
        # print("#### exec_cmp_operator", operator, left, right)
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        else:
            raise ValueError(f"Unknown operator {operator}")


class CmpOperator(ASTNode):
    """
    Represents a comparison operator node in the AST.
    """

    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        """
        Evaluate the comparison operator.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the comparison operator.
        """
        # print(f"{CmpOperator.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        operator = value
        return CmpOperator(operator=operator)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.operator}")'


class BoolUnaryOperator(ASTNode):
    """
    Represents a boolean unary operator node in the AST.
    """

    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        """
        Evaluate the boolean unary operator.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the boolean unary operator.
        """
        # print(f"{BoolUnaryOperator.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        operator = value[0]
        return BoolUnaryOperator(operator=operator)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.operator}")'


class NegateExpression(ASTNode):
    """
    Represents a negate expression node in the AST.
    """

    def __init__(self, expr):
        super().__init__([expr])
        self.expression = expr

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the negate expression.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        right = self.expression.evaluate(row)
        return self.apply("not", right)

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the negate expression.
        """
        # print(f"{NegateExpression.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        operator = value[0]
        not_opers = ["NOT", "!"]
        if (
            not isinstance(operator, BoolUnaryOperator)
            or not operator.operator in not_opers
        ):
            raise ValueError(
                f"Expected a BoolUnaryOperator, got {type(operator)} {operator}"
            )
        expr = value[1]
        return NegateExpression(expr=expr)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.expression})"

    def apply(self, operator, right):
        """
        Apply a boolean unary operator.
        """
        if operator == "not" or operator == "!":
            return not right
        else:
            raise ValueError(f"Unknown bool_unary_operator {operator}")


class BinaryExpression(ASTNode):
    """
    Represents a binary expression node in the AST.
    """

    def __init__(self, left, operator, right):
        super().__init__([left, operator, right])
        self.left = left
        self.operator = operator
        self.right = right

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the binary expression.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        left = self.left.evaluate(row)
        operator = self.operator.evaluate()
        right = self.right.evaluate(row)
        return self.apply(operator, left, right)

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the binary expression.
        """
        # print(f"{BinaryExpression.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        left = value[0]
        operator = value[1]
        right = value[2]
        return BinaryExpression(left=left, operator=operator, right=right)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left}, {self.operator}, {self.right})"

    def apply(self, operator, left, right):
        """
        Apply a boolean binary operator.
        """
        operator = operator.lower()
        if operator == "and" or operator == "&&":
            return left and right
        elif operator == "or" or operator == "||":
            return left or right
        elif operator == "xor" or operator == "^":
            return left ^ right
        else:
            raise ValueError(f"Unknown bool_binary_operator {operator}")


class BoolBinaryOperator(ASTNode):
    """
    Represents a boolean binary operator node in the AST.
    """

    def __init__(self, operator):
        super().__init__([operator])
        self.operator = operator

    def evaluate(self):
        """
        Evaluate the boolean binary operator.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.operator

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the boolean binary operator.
        """
        # print(f"{BoolBinaryOperator.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        operator = value[0]
        return BoolBinaryOperator(operator=operator)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.operator}")'


class LiteralValue(ASTNode):
    """
    Represents a literal value node in the AST.
    """

    def __init__(self, value):
        super().__init__([value])
        self.value = value

    def evaluate(self):
        """
        Evaluate the literal value.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        return self.value

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the literal value.
        """
        # print(f"{LiteralValue.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        return LiteralValue(value=value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.value}")'


class Attribute(ASTNode):
    """
    Represents an attribute node in the AST.
    """

    def __init__(self, name):
        super().__init__([name])
        self.name = name

    # pylint: disable-next=arguments-differ
    def evaluate(self, row):
        """
        Evaluate the attribute.
        """
        # print(f"#### {self.__class__.__name__}.evaluate {repr(self)}")
        try:
            return row[self.name]
        except KeyError:
            print(f"Column not found: {self.name}", file=sys.stderr)
            return None

    @staticmethod
    # pylint: disable-next=unused-argument
    def parse(string, location, tokens: pp.ParseResults) -> Self:
        """
        Parse the attribute.
        """
        # print(f"{Attribute.__name__}.parse: {repr(tokens)}")
        value = tokens[0]
        name = value[0]
        return Attribute(name=name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'
