from error import ErrorPacket

# class which holds token data
class Token(ErrorPacket):
    NUMBER = "num"
    STRING = "str"
    TERM_OP = "term_op"
    FACTOR_OP = "factor_op"
    LOGICAL_OP = "logical_op"
    CONDITIONAL_OP = "conditional_op"
    IDENTIFIER = "identifier"
    TRUE = "true"
    FALSE = "false"
    NOVALUE = "novalue"
    SEMI_COLON = ";"
    EXCLAMATION = "!"
    COMMA = ","
    
    INCLUDE = "include"
        
    OPEN_PAREN = "("
    CLOSED_PAREN = ")"
    
    OPEN_SQUARE = "["
    CLOSED_SQUARE = "]"

    OPEN_CURLY = "{"
    CLOSED_CURLY = "}"

    KEYWORD = "keyword"
    ASSIGNMENT_OP = "ass_op"
    
    POINT = "."

    EOF = "eof"

    keywords = ["if", "else", "stop", "skip", "while", "for", "return", "print", "var", "fun", "input"]

    def __init__(self, t, lexeme: str):
        self.type = t
        self.lexeme = lexeme
