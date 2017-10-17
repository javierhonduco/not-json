from enum import Enum

# Toy parser for a JSON subset to learn more about compilers :)


UNARY_OPS = ('+', '-')


class Tokens(Enum):
    STRING = 0
    NUMBER = 1
    L_SQUARE_BRACKET = 2
    R_SQUARE_BRACKET = 3
    L_CURLY_BRACE = 4
    R_CURLY_BRACE = 5
    COLON = 6
    COMMA = 7
    BOOLEAN = 8
    NULL = 9
    EOF = 10


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return 'Token({}, {})'.format(self.type, self.value)

    def __eq__(self, other):
        if self.type == other.type and self.value == other.value:
            return True
        return False


RESERVED_KEYWORDS = {
    'true': Token(Tokens.BOOLEAN, 'true'),
    'false': Token(Tokens.BOOLEAN, 'false'),
    'null': Token(Tokens.NULL, 'null'),
}


class LexerError(Exception):
    pass


class KeywordError(LexerError):
    pass


class ParserError(Exception):
    pass


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def consume(self):
        current_char = self.current_char
        self.advance()
        return current_char

    def error(self):
        raise LexerError(
            'Unrecognized char="{}" found at pos={}'.format(
                self.current_char,
                self.pos,
            )
        )

    def whitespaces(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def digit(self):
        # This function is a bit too basic, only parses positive and negative
        # integers anf floats which are not expressed in scientific form  and
        # doesn't handle cases such as multiple consecutive unary ops such as
        # ----1
        accum = ''
        is_float = False

        if self.current_char is not None and self.current_char in UNARY_OPS:
            accum += self.current_char
            self.advance()

        while self.current_char is not None and self.current_char.isdigit():
            accum += self.current_char
            self.advance()

        if self.current_char is not None and self.current_char in '.':
            accum += self.current_char
            self.advance()
            is_float = True

        while self.current_char is not None and self.current_char.isdigit():
            accum += self.current_char
            self.advance()

        if is_float:
            return float(accum)
        return int(accum)

    def reserved(self):
        accum = ''
        while self.current_char is not None and self.current_char.isalpha():
            accum += self.current_char
            self.advance()

        try:
            return RESERVED_KEYWORDS[accum]
        except KeyError:
            raise KeywordError(
                'Reserved keyword {} does not exist'.format(accum)
            )

    def string(self):
        self.consume()  # Consumes the opening double quote
        accum = ''
        while self.current_char is not None and self.current_char != '"':
            accum += self.current_char
            self.advance()
        self.consume()  # Consumes the closing double quote
        return accum

    def next_token(self):
        if self.current_char is None:
            return Token(Tokens.EOF, 'EOF')

        if self.current_char.isspace():
            self.whitespaces()

        if self.current_char == '"':
            return Token(Tokens.STRING, self.string())

        if self.current_char.isalpha():
            return self.reserved()

        if self.current_char.isdigit() or self.current_char in UNARY_OPS:
            return Token(Tokens.NUMBER, self.digit())

        if self.current_char == '[':
            return Token(Tokens.L_SQUARE_BRACKET, self.consume())

        if self.current_char == ']':
            return Token(Tokens.R_SQUARE_BRACKET, self.consume())

        if self.current_char == '{':
            return Token(Tokens.L_CURLY_BRACE, self.consume())

        if self.current_char == '}':
            return Token(Tokens.R_CURLY_BRACE, self.consume())

        if self.current_char == '{':
            return Token(Tokens.L_CURLY_BRACE, self.consume())

        if self.current_char == '}':
            return Token(Tokens.R_CURLY_BRACE, self.consume())

        if self.current_char == ':':
            return Token(Tokens.COLON, self.consume())

        if self.current_char == ',':
            return Token(Tokens.COMMA, self.consume())

        self.error()

    def all_tokens(self):
        tokens = []
        while True:
            token = self.next_token()
            if token.type is Tokens.EOF:
                return tokens
            tokens.append(token)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def eat(self, expected_type):
        if self.current_token.type == expected_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error(expected_type)

    def error(self, expected):
        raise ParserError('Found "{}" when expecting "{}"'.format(
            self.current_token,
            expected,
        ))

    def number(self):
        '''
        number  :   NUMBER
        '''
        token = self.current_token
        self.eat(Tokens.NUMBER)
        return token.value

    def boolean(self):
        '''
        boolean :   TRUE | FALSE
        '''
        token = self.current_token
        self.eat(Tokens.BOOLEAN)

        if token.value == 'true':
            return True
        elif token.value == 'false':
            return False
        return token.value

    def null(self):
        '''
        null:   null
        '''
        self.eat(Tokens.NULL)
        return None

    def string(self):
        '''
        string  :   STRING
        '''

        token = self.current_token
        self.eat(Tokens.STRING)

        return token.value

    def key(self):
        '''
        key    : number | string
        '''
        token = self.current_token
        if token.type == Tokens.NUMBER:
            self.eat(Tokens.NUMBER)
        elif token.type == Tokens.STRING:
            self.eat(Tokens.STRING)

        return token.value

    def pair(self):
        '''
        pair    :
            key COLON expr
        '''
        key = self.key()
        self.eat(Tokens.COLON)
        value = self.expr()

        return (key, value)

    def object(self):
        '''
        object  :
            L_CURLY_BRACE R_CURLY_BRACE
            | L_CURLY_BRACE pair (, pair)+ R_CURLY_BRACE
        '''
        result = {}

        self.eat(Tokens.L_CURLY_BRACE)
        if self.current_token.type != Tokens.R_CURLY_BRACE:
            key, value = self.pair()
            result[key] = value

        while self.current_token.type == Tokens.COMMA:
            self.eat(Tokens.COMMA)
            key, value = self.pair()
            result[key] = value

        self.eat(Tokens.R_CURLY_BRACE)

        return result

    def array(self):
        '''
        array   :
            L_SQUARE_BRACKET R_SQUARE_BRACKET
            | L_SQUARE_BRACKET expr (, expr)+ R_SQUARE_BRACKET
        '''
        result = []

        self.eat(Tokens.L_SQUARE_BRACKET)

        if self.current_token.type not in (
            Tokens.COMMA,
            Tokens.R_SQUARE_BRACKET,
        ):
            result.append(self.expr())

        while self.current_token.type == Tokens.COMMA:
            self.eat(Tokens.COMMA)
            result.append(self.expr())

        self.eat(Tokens.R_SQUARE_BRACKET)

        return result

    def expr(self):
        '''
        expr    :   object | array | string | number | boolean | null
        '''
        if self.current_token.type == Tokens.L_CURLY_BRACE:
            return self.object()

        if self.current_token.type == Tokens.L_SQUARE_BRACKET:
            return self.array()

        if self.current_token.type == Tokens.STRING:
            return self.string()

        if self.current_token.type == Tokens.BOOLEAN:
            return self.boolean()

        if self.current_token.type == Tokens.NULL:
            return self.null()

        if self.current_token.type == Tokens.NUMBER:
            return self.number()

        self.error('object | array | string | true | false | null | number')

    def parse(self, strict=True):
        self.current_token = self.lexer.next_token()
        expr = self.expr()
        if strict:
            # To consume the End Of File marker
            self.eat(Tokens.EOF)
        return expr
