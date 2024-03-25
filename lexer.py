from tokens import *
from error import *
import os


# handles lexing of multiple files
class MultiFileLexer:
    def __init__(self, init_path):
        self.tokens = []
        self.added = []
        self.lex(init_path)

    def lex(self, path):
        lexer = Lexer(path)
        lexer.lex()

        if len(self.tokens) > 0:
            lexer.tokens.pop()  # get rid of EOF

        self.tokens = lexer.tokens + self.tokens
        for include in lexer.includes:
            path = include.lexeme
            if path in self.added:
                continue
            if not os.path.isfile(path):
                Error.report_packet(f"file with path '{path}' doesn't exist.", include)
                continue

            self.lex(path)


# check if a character is a hex digit
def ishex(x):
    return x in '0123456789abcdefABCDEF'


# lexer or tokeniser, which tokenises the raw string of the program file
class Lexer:

    def __init__(self, path):
        self.path = path
        with open(path, "r") as file:
            self.string = file.read()

        self.i = 0

        Error.raw_lines[path] = self.string.split("\n")

        self.line = 1
        self.char_index = 0

        self.tokens = []

        self.includes = []

    def lex(self):
        # set error stage
        Error.stage = "Lexing"

        while not self.is_end():
            char = self.current()

            # when we hit a newline, we increment the line and reset char_index
            # this is purely for debugging
            if char == "\n":
                self.line += 1
                self.char_index = -1

                self.advance()
                continue

            if self.char_index == 0 and char == "#":
                self.handle_include()
                continue

            if char == "\r" or char == " ":
                self.advance()
                continue

            if char == "/" and self.check_next("/"):
                # we need to make room for comments
                self.ignore_comment()
                continue

            if char == "*" or char == "/":
                if self.check_next("="):
                    self.add_token(Token.ASSIGNMENT_OP, char)
                else:
                    self.add_token(Token.FACTOR_OP)
                self.advance()
                continue

            if char == "+" or char == "-":
                if self.check_next("="):
                    self.add_token(Token.ASSIGNMENT_OP, char)
                else:
                    self.add_token(Token.TERM_OP)
                self.advance()
                continue

            if char == "=":
                if self.check_next("="):
                    self.add_token(Token.CONDITIONAL_OP, "==")
                else:
                    self.add_token(Token.ASSIGNMENT_OP, "")

                self.advance()
                continue

            if char == ">" or char == "<":
                if self.check_next("="):
                    self.add_token(Token.CONDITIONAL_OP, self.previous() + "=")
                else:
                    self.add_token(Token.CONDITIONAL_OP)

                self.advance()
                continue

            if char == ";":
                self.add_token(Token.SEMI_COLON, "")
                self.advance()
                continue

            if char == "!":
                if self.check_next("="):
                    self.add_token(Token.CONDITIONAL_OP, "!=")
                else:
                    self.add_token(Token.EXCLAMATION, "")

                self.advance()
                continue

            if char == ',':
                self.add_token(Token.COMMA, "")
                self.advance()
                continue

            if char == '.':
                self.add_token(Token.POINT, "")
                self.advance()
                continue

            if char == '(':
                self.add_token(Token.OPEN_PAREN, "")
                self.advance()
                continue

            if char == ')':
                self.add_token(Token.CLOSED_PAREN, "")
                self.advance()
                continue

            if char == '{':
                self.add_token(Token.OPEN_CURLY, "")
                self.advance()
                continue

            if char == '}':
                self.add_token(Token.CLOSED_CURLY, "")
                self.advance()
                continue

            if char == '[':
                self.add_token(Token.OPEN_SQUARE, "")
                self.advance()
                continue

            if char == ']':
                self.add_token(Token.CLOSED_SQUARE, "")
                self.advance()
                continue

            if char == '"':
                self.lex_string()
                continue

            # has to come before lex id
            if char.isdigit():
                self.lex_number()
                continue

            if self.is_id_char(char):
                self.lex_id()
                continue

            Error.report(f"Unexpected character '{char}'", self.line, self.char_index, self.path)
            self.advance()

        self.add_token(Token.EOF, "")
        return self.tokens

    def advance(self):
        self.i += 1
        self.char_index += 1

    def current(self):
        return self.string[self.i]

    def check_next(self, n):
        if self.i + 1 >= len(self.string):
            return False

        if n == self.string[self.i + 1]:
            self.advance()
            return True

        return False

    def previous(self):
        return self.string[self.i - 1]

    def lex_number(self):
        num = self.current()
        start_index = self.char_index
        self.advance()

        while not self.is_end() and self.current().isdigit():
            num += self.current()
            self.advance()

        if not self.is_end() and self.current() == '.':
            num += "."
            self.advance()

            while not self.is_end() and self.current().isdigit():
                num += self.current()
                self.advance()

        self.add_token(Token.NUMBER, num, self.line, start_index)

    def lex_string(self):
        start_index = self.char_index

        self.advance()
        string = ""

        closed_string = True

        while self.current() != '"':
            char: str = self.current()
            if char == "\\":
                self.advance()

                if self.is_end() or self.current() in ["\n", "\r"]:
                    closed_string = False
                    break

                char = self.current()
                if char == "n":
                    char = "\n"

                elif char == "t":
                    char = "\t"

                elif char == "r":
                    char = "\r"

                elif char == "\"":
                    char = "\""

                elif char == "\\":
                    char = "\\"

                elif ishex(char):
                    value = char

                    self.advance()
                    char = self.current()
                    value += char

                    if ishex(char):
                        char = chr(int(value, 16))
                    else:
                        Error.report(f"invalid hex number '{value}' found in string. needs to be 2 digits", self.line,
                                     self.char_index, self.path)

                else:
                    Error.report(f"invalid escape character '\\{char}'", self.line, self.char_index, self.path)

            string += char
            self.advance()

            if self.is_end() or self.current() in ["\n", "\r"]:
                closed_string = False
                break

        if closed_string:
            self.advance()
        else:
            Error.report("Start of unclosed string", self.line, start_index, self.path)

        self.add_token(Token.STRING, string, self.line, start_index)

    def is_id_char(self, c: str):
        return c.isalnum() or c == '_'

    def lex_id(self):
        id = self.current()
        start_index = self.char_index
        self.advance()

        while not self.is_end() and self.is_id_char(self.current()):
            id += self.current()
            self.advance()

        if id == "true":
            self.add_token(Token.TRUE, "", self.line, start_index)
            return

        if id == "false":
            self.add_token(Token.FALSE, "", self.line, start_index)
            return

        if id == "novalue":
            self.add_token(Token.NOVALUE, "", self.line, start_index)
            return

        if id == "and" or id == "or":
            self.add_token(Token.LOGICAL_OP, id, self.line, start_index)
            return

        if id in Token.keywords:
            self.add_token(Token.KEYWORD, id, self.line, start_index)
            return

        self.add_token(Token.IDENTIFIER, id, self.line, start_index)

    def ignore_comment(self):
        while not self.is_end() and self.current() not in ["\n", "\r"]:
            self.advance()

    def handle_include(self):
        self.advance()  # skip over #
        char_index = self.char_index
        path = ""
        while not self.is_end() and self.current() not in ["\n", "\r"]:
            path += self.current()
            self.advance()

        self.includes.append(Token(Token.INCLUDE, path).set_error_fields(self.line, char_index, self.path))

    def add_token(self, token_type, lexeme=None, line=None, char_index=None):
        if lexeme is None:
            lexeme = self.current()

        if line == None:
            line = self.line

        if char_index == None:
            char_index = self.char_index

        self.tokens.append(Token(token_type, lexeme).set_error_fields(line, char_index, self.path))

    def is_end(self):
        return self.i >= len(self.string)
