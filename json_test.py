import unittest

from json import (
    KeywordError,
    Lexer,
    Parser,
    ParserError,
    Token,
    Tokens,
)


class LexerTest(unittest.TestCase):
    def test_basic_lexer(self):
        self.maxDiff = None
        code = '{2: [], "lol": {"omg": {"so": {"deep": []}}}}'
        tokens = Lexer(code).all_tokens()
        expected = [
            Token(Tokens.L_CURLY_BRACE, '{'),
            Token(Tokens.NUMBER, 2),
            Token(Tokens.COLON, ':'),
            Token(Tokens.L_SQUARE_BRACKET, '['),
            Token(Tokens.R_SQUARE_BRACKET, ']'),
            Token(Tokens.COMMA, ','),
            Token(Tokens.STRING, 'lol'),
            Token(Tokens.COLON, ':'),
            Token(Tokens.L_CURLY_BRACE, '{'),
            Token(Tokens.STRING, 'omg'),
            Token(Tokens.COLON, ':'),
            Token(Tokens.L_CURLY_BRACE, '{'),
            Token(Tokens.STRING, 'so'),
            Token(Tokens.COLON, ':'),
            Token(Tokens.L_CURLY_BRACE, '{'),
            Token(Tokens.STRING, 'deep'),
            Token(Tokens.COLON, ':'),
            Token(Tokens.L_SQUARE_BRACKET, '['),
            Token(Tokens.R_SQUARE_BRACKET, ']'),
            Token(Tokens.R_CURLY_BRACE, '}'),
            Token(Tokens.R_CURLY_BRACE, '}'),
            Token(Tokens.R_CURLY_BRACE, '}'),
            Token(Tokens.R_CURLY_BRACE, '}'),
        ]
        self.assertEqual(tokens, expected)


class ParserTest(unittest.TestCase):
    def test_empty_object(self):
        code = '{}'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, {})

    def test_object_one_pair(self):
        code = '{1: 2}'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, {1: 2})

    def test_object_multiple_pairs(self):
        code = '{1:2, 3:4}'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, {1: 2, 3: 4})

    def test_empty_array(self):
        code = '[]'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, [])

    def test_array_one_element(self):
        code = '[1]'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, [1])

    def test_array_multiple_elements(self):
        code = '[1, 2]'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, [1, 2])

    def test_true(self):
        code = 'true'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, True)

    def test_false(self):
        code = 'false'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, False)

    def test_false(self):
        code = 'false'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, False)

    def test_null(self):
        code = 'null'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, None)

    def test_positive_integer(self):
        code = '314'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, 314)

    def test_positive_integer(self):
        code = '314'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, 314)

    def test_negative_integer(self):
        code = '-314'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, -314)

    def test_positive_float(self):
        code = '3.14'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, 3.14)

    def test_negative_float(self):
        code = '-3.14'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, -3.14)

    def test_string(self):
        code = '"omg_kittens"'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, "omg_kittens")

    def test_complex_array(self):
        code = '[true, false, null, "lol", {"key": [{}, []]}]'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, [True, False, None, 'lol', {'key': [{}, []]}])

    def test_complex_object(self):
        code = '{2: [], "lol": {"omg": {"so": {"deep": []}}}}'
        result = Parser(Lexer(code)).parse()
        self.assertEqual(result, {2: [], 'lol': {'omg': {'so': {'deep': []}}}})

    def test_invalid_syntax_solo_comma(self):
        with self.assertRaises(ParserError):
            result = Parser(Lexer(',')).parse()

    def test_invalid_syntax_array_key(self):
        with self.assertRaises(ParserError):
            result = Parser(Lexer('{[]: "no"}')).parse()

    def test_invalid_syntax_array_consume_eof(self):
        with self.assertRaises(ParserError):
            result = Parser(Lexer('[][]')).parse()

    def test_invalid_keyword(self):
        with self.assertRaises(KeywordError):
            result = Parser(Lexer('falsey')).parse()

if __name__ == '__main__':
    unittest.main()
