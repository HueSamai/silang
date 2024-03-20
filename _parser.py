from tokens import *
from error import *
from tree_components import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def parse(self):
        Error.stage = "Parsing"

        stmts = []
        while not self.is_end():
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)

        if not Error.error_occurred:
            return stmts
        
        return []

    @staticmethod
    def tree_to_str(head):
        if head is None:
            return "<error>"

        if type(head) is Literal:
            return Parser.get_value(head.lvalue)
        
        if type(head) is Variable:
            return head.lvalue

        if type(head) is BinaryExpression:
            return f"({head.op} {Parser.tree_to_str(head.lvalue)} {Parser.tree_to_str(head.rvalue)})"
        
        if type(head) is Call:
            return f"({Parser.tree_to_str(head.callee)} {', '.join([Parser.tree_to_str(arg) for arg in head.args])})"

        if type(head) is Unary:
            return f"({head.op} {Parser.tree_to_str(head.lvalue)})"

    @staticmethod
    def get_value(val):
        if val is None:
                return "novalue"

        if type(val) == bool:
            return "true" if val else "false"

        if type(val) == float and val == int(val):
            return str(int(val))
        
        if type(val) is list:
            return "[" + ', '.join([Parser.get_value(item) for item in val]) + "]"
        
        if type(val) is SILString:
            return val.get_string().encode('ascii', errors='replace').decode('ascii')

        return f"{val}"

    def previous(self):
        return self.tokens[self.i - 1]

    def current(self):
        return self.tokens[self.i]

    def advance(self):
        self.i += 1

    def match(self, token_type, lexeme=None):
        if self.is_end():
            return False

        current = self.current()
        if current.type != token_type:
            return False

        if lexeme is not None and current.lexeme != lexeme:
            return False
        
        return True
    
    def peek(self, token_type, lexeme=None):
        if self.i + 1 >= len(self.tokens):
            return False

        if self.tokens[self.i + 1].type != token_type:
            return False

        if lexeme is not None and self.tokens[self.i + 1].lexeme != lexeme:
            return False
        
        return True
    
    def consume(self, token_type, lexeme=None):
        if self.match(token_type, lexeme):
            self.advance()
            return
        
        current = self.current()

        self.report_error(f"Expected '{token_type}' but got '{current.type}' instead", current)
        self.advance()

    def report_error(self, message, packet):
        Error.report_packet(message, packet)
        self.correct_error()

    def set_error_fields(self, to, _from):
        if not Error.error_occurred:
            to.set_error_fields(_from.line, _from.char_index, _from.file)
        return to

    def is_end(self):
        return self.i >= len(self.tokens) or self.current().type == Token.EOF
    
    def parse_statement(self):
        if self.match(Token.KEYWORD, "print"):
            return self.parse_print()
        
        if self.match(Token.KEYWORD, "fun"):
            return self.parse_function()
        
        if self.match(Token.KEYWORD, "return"):
            return self.parse_return()
        
        if self.match(Token.KEYWORD, "skip"):
            return self.parse_skip()
        
        if self.match(Token.KEYWORD, "stop"):
            return self.parse_stop()
        
        if self.match(Token.KEYWORD, "var"):
            return self.parse_var_decl()
        
        if self.match(Token.KEYWORD, "while"):
            return self.parse_while()
        
        if self.match(Token.KEYWORD, "for"):
            return self.parse_for()

        if self.match(Token.IDENTIFIER) and self.peek(Token.ASSIGNMENT_OP):
            return self.parse_var_set()
        
        if self.match(Token.IDENTIFIER) and self.peek(Token.OPEN_SQUARE):
            return self.parse_list_set()

        if self.match(Token.OPEN_CURLY):
            return self.parse_block()
        
        if self.match(Token.KEYWORD, "if"):
            return self.parse_if()

        return self.parse_expr_stmt()
        
    def parse_expr_stmt(self):
        if self.match(Token.SEMI_COLON):
            self.advance()
            return None

        current = self.current()
        expression = self.parse_expression()
        self.consume(Token.SEMI_COLON)
        return self.set_error_fields(Statement(Statement.FLAT, expression), current)

    def parse_if(self):
        current = self.current()
        self.advance() # skip over if

        expr = self.parse_expression()
        stmt = self.parse_statement()
        elseStmt = None

        if self.match(Token.KEYWORD, "else"):
            self.advance()
            elseStmt = self.parse_statement()

        return self.set_error_fields(If(expr, stmt, elseStmt), current)

    def parse_print(self):
        current = self.current()

        self.advance()
        expression = self.parse_expression()
        self.consume(Token.SEMI_COLON)
        return self.set_error_fields(Statement(Statement.PRINT, expression), current)

    def parse_return(self):
        current = self.current()
        self.advance()

        expression = self.set_error_fields(Literal(None), current)
        if not self.match(Token.SEMI_COLON):
            expression = self.parse_expression()
        self.consume(Token.SEMI_COLON)

        return self.set_error_fields(Return(expression), current)
    
    def parse_stop(self):
        current = self.current()
        self.advance()

        expr = None
        if not self.match(Token.SEMI_COLON):
            expr = self.parse_expression()
        self.consume(Token.SEMI_COLON)

        thingy = self.set_error_fields(Stop(), current)
        if expr is not None:
            thingy = self.set_error_fields(If(expr, thingy, None), current)
        return thingy
    
    def parse_skip(self):
        current = self.current()
        self.advance()

        expr = None
        if not self.match(Token.SEMI_COLON):
            expr = self.parse_expression()
        self.consume(Token.SEMI_COLON)

        thingy = self.set_error_fields(Skip(), current)
        if expr is not None:
            thingy = self.set_error_fields(If(expr, thingy, None), current)
        return thingy

    def parse_while(self):
        current = self.current()
        self.advance() # skip over while

        expr = self.parse_expression()
        stmt = self.parse_statement()

        return self.set_error_fields(While(expr, stmt), current)
    
    def parse_for(self):
        current = self.current()
        self.advance() # skip over for
        
        init_stmt = None
        if self.match(Token.KEYWORD, "var"):
            init_stmt = self.parse_var_decl()
        elif self.match(Token.IDENTIFIER):
            init_stmt = self.parse_var_set()
        else:
            self.consume(Token.SEMI_COLON)
        
        scnd_stmt = None
        if not self.match(Token.SEMI_COLON):
            scnd_stmt = self.parse_expression()
        self.consume(Token.SEMI_COLON)

        last_stmt = self.parse_statement()

        stmt = self.parse_statement()
        if stmt is None:
            stmt = self.set_error_fields(Statement(Statement.FLAT, Literal(None)), current)

        stmts = []
        if init_stmt is not None:
            stmts.append(init_stmt)
        
        stmts.append(self.set_error_fields(
            While(scnd_stmt if scnd_stmt else Literal(True), stmt, last_stmt), 
            scnd_stmt if scnd_stmt else current)
        )

        return self.set_error_fields(
            Block(stmts),
            current
        )
    
    def parse_params(self):
        params = []
        if self.match(Token.CLOSED_PAREN):
            return params
        
        id = self.current().lexeme
        self.consume(Token.IDENTIFIER)
        params.append(id)

        while self.match(Token.COMMA):
            self.advance()
            id = self.current().lexeme
            self.consume(Token.IDENTIFIER)
            params.append(id)

        return params

    def parse_function(self):

        self.advance() # skip over fun keyword

        id = self.current().lexeme
        current = self.current()
        self.consume(Token.IDENTIFIER)

        self.consume(Token.OPEN_PAREN)
        params = self.parse_params()
        self.consume(Token.CLOSED_PAREN)

        stmt = self.parse_statement()
        
        if stmt.type == Statement.FLAT:
            stmt = self.set_error_fields(Return(stmt.expr), stmt)
        
        if stmt.type != Statement.BLOCK:
            stmt: Block = self.set_error_fields(Block([stmt]), stmt)

        return self.set_error_fields(Function(id, params, stmt), current)


    def parse_block(self):
        current = self.current()

        self.advance() # skip over curly bracket

        stmts = []
        while not self.is_end() and self.current().type != Token.CLOSED_CURLY:
            stmts.append(self.parse_statement())

        self.consume(Token.CLOSED_CURLY)

        return self.set_error_fields(Block(stmts), current)


    def parse_var_decl(self):
        current = self.current()
        self.advance() # skip over var keyword

        id = self.current().lexeme
        self.consume(Token.IDENTIFIER)

        expression = None
        if self.match(Token.ASSIGNMENT_OP, ""):
            self.advance()
            expression = self.parse_expression()
        else:
            expression = self.set_error_fields(Literal(None), current)

        self.consume(Token.SEMI_COLON)
        return self.set_error_fields(VarDecl(id, expression), current)
   

    def parse_var_set(self):
        current = self.current()
        id = current.lexeme

        # skip over var keyword
        self.advance()
        
        op = self.current().lexeme
        self.consume(Token.ASSIGNMENT_OP)

        expression = self.parse_expression()
        self.consume(Token.SEMI_COLON)
            
        if op != "":
            expression = self.set_error_fields(BinaryExpression(Variable(id), expression, op), current)

        return self.set_error_fields(VarSet(id, expression), current)
   
    def parse_list_set(self):
        current = self.current()
        id = current.lexeme
        
        # skip over identifier
        self.advance()

        lst = self.set_error_fields(Variable(id), current)
        index_expr = None

        while True:
            self.advance() # skip over [
            index_expr = self.parse_expression()
            self.consume(Token.CLOSED_SQUARE)
            if self.match(Token.OPEN_SQUARE):
                lst = self.set_error_fields(ListAccess(id, index_expr), lst)
            else:
                break
        
        op = self.current().lexeme
        self.consume(Token.ASSIGNMENT_OP)
        
        expr = self.parse_expression()
        self.consume(Token.SEMI_COLON)

        if op != "":
            expression = self.set_error_fields(BinaryExpression(Variable(id), expression, op), current)

        return self.set_error_fields(ListSet(lst, index_expr, expr), current)


    def parse_expression(self):
        return self.parse_logic()

    def parse_logic(self):
        lvalue = self.parse_conditional()

        while not self.is_end() and self.match(Token.LOGICAL_OP):
            current = self.current()
            op = current.lexeme
            self.advance()

            lvalue = self.set_error_fields(BinaryExpression(lvalue, self.parse_conditional(), op), current)
        
        return lvalue

    def parse_conditional(self):
        lvalue = self.parse_term()

        while not self.is_end() and self.match(Token.CONDITIONAL_OP):
            current = self.current()
            op = current.lexeme
            self.advance()

            lvalue = self.set_error_fields(BinaryExpression(lvalue, self.parse_term(), op), current)
        
        return lvalue
    

    def parse_term(self):
        lvalue = self.parse_factor()

        while not self.is_end() and self.match(Token.TERM_OP):
            current = self.current()
            op = current.lexeme
            self.advance()

            lvalue = self.set_error_fields(BinaryExpression(lvalue, self.parse_factor(), op), current)
        
        return lvalue

    def parse_factor(self):
        lvalue = self.parse_unary()

        while not self.is_end() and self.match(Token.FACTOR_OP):
            current = self.current()
            op = current.lexeme
            self.advance()

            lvalue = self.set_error_fields(BinaryExpression(lvalue, self.parse_unary(), op), current)
        
        return lvalue

    def parse_unary(self):
        if self.match(Token.EXCLAMATION) or self.match(Token.TERM_OP, "-"):
            op =  "!" if self.match(Token.EXCLAMATION) else "-"
            current = self.current()
            self.advance()

            return self.set_error_fields(Unary(op, self.parse_list_access()), current)
        
        current = self.current()
        return self.set_error_fields(self.parse_list_access(), current)


    def parse_list_access(self):
        lst = self.parse_call()

        while self.match(Token.OPEN_SQUARE):
            self.advance()
            index_expr = self.parse_expression()
            self.consume(Token.CLOSED_SQUARE)
            lst = self.set_error_fields(ListAccess(lst, index_expr), lst)
        
        return lst


    def parse_expr_list(self, end_token=Token.CLOSED_PAREN):
        args = []
        if not self.match(end_token):
            args.append(self.parse_expression())
            while self.match(Token.COMMA):
                self.advance()
                args.append(self.parse_expression())

        return args

    def parse_call(self):
        current = self.current()

        call = self.set_error_fields(self.parse_primary(), current)
        
        is_weird = False
        id = None
        if self.match(Token.POINT):
            self.advance()
            id = self.current().lexeme
            self.consume(Token.IDENTIFIER)
            is_weird = True
        
        saw_paren = False
        while self.match(Token.OPEN_PAREN):
            saw_paren = True
            self.advance()
            arguments = self.parse_expr_list()
            self.consume(Token.CLOSED_PAREN)
            if is_weird:
                is_weird = False
                arguments.insert(0, call)
                call = Variable(id)
            call = self.set_error_fields(Call(call, arguments), current)
            
        if is_weird and not saw_paren:
            self.report_error("Weird function call requires parenthesis", call)

        return call

    def parse_primary(self):
        if self.is_end():
            self.report_error("Expected primary after", self.previous())
            return None

        lexeme = self.current().lexeme

        if self.match(Token.KEYWORD, "input"):
            self.advance()
            expr = self.parse_expression()

            return Input(expr)

        if self.match(Token.IDENTIFIER):
            self.advance()
            return Variable(lexeme)

        if self.match(Token.STRING):
            self.advance()
            return Literal(SILString(lexeme))
        
        if self.match(Token.NUMBER):
            self.advance()
            return Literal(float(lexeme))
        
        if self.match(Token.TRUE):
            self.advance()
            return Literal(True)
        
        if self.match(Token.FALSE):
            self.advance()
            return Literal(False)
        
        if self.match(Token.OPEN_SQUARE):
            self.advance()
            lst = self.parse_expr_list(Token.CLOSED_SQUARE)
            self.consume(Token.CLOSED_SQUARE)
            return Literal(lst)

        if self.match(Token.NOVALUE):
            self.advance()
            return Literal(None)
        
        if self.match(Token.OPEN_PAREN):
            self.advance()
            value = self.parse_expression()
            self.consume(Token.CLOSED_PAREN)

            return value
        
        lexeme = self.current().lexeme
        self.report_error(f"Expected primary but got '{self.current().type}{' ' if lexeme != '' else ''}{lexeme}' ", self.current())

    def correct_error(self):
        while not self.is_end():
            if self.match(Token.SEMI_COLON):
                break

            if self.match(Token.CLOSED_CURLY):
                break

            self.advance()


        
        
