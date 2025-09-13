import unittest

from query.parser import Parser, ParserException


class TestParser(unittest.TestCase):
    def test_literal_string_starting_with_uppercase(self):
        query = ".Avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("Avg")), CmpOperator("=="), LiteralValue("0.5"))))'
        self.assertEqual(repr(ast), expected)

    def test_literal_string_starting_with_underscore(self):
        query = "._avg == 0.5"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("_avg")), CmpOperator("=="), LiteralValue("0.5"))))'
        self.assertEqual(repr(ast), expected)

    def test_literal_string_starting_with_plussign(self):
        query = ".+avg == 0.5"
        parser = Parser(query)
        with self.assertRaises(ParserException) as ctx:
            parser.parse()
        self.assertEqual(str(ctx.exception), "Query syntax error at line 1 col 2")

    def test_literal_string_starting_with_number(self):
        query = ".123 == 0.5"
        parser = Parser(query)
        with self.assertRaises(ParserException) as ctx:
            parser.parse()
        self.assertEqual(str(ctx.exception), "Query syntax error at line 1 col 2")

    def test_single_quoted_string_literal(self):
        query = ".name == 'hello'"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue("hello"))))'
        self.assertEqual(repr(ast), expected)

    def test_double_quoted_string_literal(self):
        query = '.name == "hello"'
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue("hello"))))'
        self.assertEqual(repr(ast), expected)

    def test_single_quoted_string_with_spaces(self):
        query = ".name == 'hello world'"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue("hello world"))))'
        self.assertEqual(repr(ast), expected)

    def test_single_quoted_string_with_numbers(self):
        query = ".code == 'ABC123'"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("code")), CmpOperator("=="), LiteralValue("ABC123"))))'
        self.assertEqual(repr(ast), expected)

    def test_single_quoted_string_with_special_chars(self):
        query = ".name == 'user@domain.com'"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue("user@domain.com"))))'
        self.assertEqual(repr(ast), expected)

    def test_empty_single_quoted_string(self):
        query = ".name == ''"
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue(""))))'
        self.assertEqual(repr(ast), expected)

    def test_empty_double_quoted_string(self):
        query = '.name == ""'
        parser = Parser(query)
        ast = parser.parse()
        expected = 'Grammar(Expression(Comparison(Identifier(Attribute("name")), CmpOperator("=="), LiteralValue(""))))'
        self.assertEqual(repr(ast), expected)


if __name__ == "__main__":
    unittest.main()
