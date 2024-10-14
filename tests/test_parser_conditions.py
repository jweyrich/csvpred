import unittest

from query.parser import Parser, ParserException


class TestParserConditions(unittest.TestCase):
    def test_single_condition_gte(self):
        query = ".avg >= 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'ParseResults([Grammar(Expression(Comparison(Identifier(Attribute("avg")), CmpOperator(">="), LiteralValue("0.5"))))], {})'
        self.assertEqual(repr(ast), expected)

    def test_single_condition_eq(self):
        query = ".avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'ParseResults([Grammar(Expression(Comparison(Identifier(Attribute("avg")), CmpOperator("=="), LiteralValue("0.5"))))], {})'
        self.assertEqual(repr(ast), expected)

    def test_single_negated_condition_eq(self):
        query = "not .avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'ParseResults([Grammar(Expression(NegateExpression(Expression(Comparison(Identifier(Attribute("avg")), CmpOperator("=="), LiteralValue("0.5"))))))], {})'
        self.assertEqual(repr(ast), expected)

    def test_invalid_condition_operator_eq(self):
        query = ".avg = 0.5"
        parser = Parser(query)
        with self.assertRaises(ParserException) as ctx:
            parser.parse()
        self.assertEqual(str(ctx.exception), "Query syntax error at line 1 col 6")


if __name__ == "__main__":
    unittest.main()
