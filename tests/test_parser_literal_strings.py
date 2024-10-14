import unittest

from query.parser import Parser, ParserException


class TestParser(unittest.TestCase):
    def test_literal_string_starting_with_uppercase(self):
        query = ".Avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'ParseResults([Grammar(Expression(Comparison(Identifier(Attribute("Avg")), CmpOperator("=="), LiteralValue("0.5"))))], {})'
        self.assertEqual(repr(ast), expected)

    def test_literal_string_starting_with_underscore(self):
        query = "._avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'ParseResults([Grammar(Expression(Comparison(Identifier(Attribute("_avg")), CmpOperator("=="), LiteralValue("0.5"))))], {})'
        self.assertEqual(repr(ast), expected)

    def test_literal_string_starting_with_plussign(self):
        query = ".+avg == 0.5"
        parser = Parser(query)
        with self.assertRaises(ParserException) as ctx:
            parser.parse()
        self.assertEqual(str(ctx.exception), "Query syntax error at line 1 col 1")

    def test_literal_string_starting_with_number(self):
        query = ".123 == 0.5"
        parser = Parser(query)
        with self.assertRaises(ParserException) as ctx:
            parser.parse()
        self.assertEqual(str(ctx.exception), "Query syntax error at line 1 col 1")


if __name__ == "__main__":
    unittest.main()
