from error import ErrorPacket
from environment import *
from typing import Any


class SILStringNotChar(Exception):
    pass


class SILString:
    def __init__(self, string):
        self.string = list(string)

    def is_not_char(self, item):
        return type(item) is not SILString or len(item) != 1

    def get_string(self):
        return ''.join(self.string)

    def __getitem__(self, index):
        return SILString(self.string[index])

    def __setitem__(self, index, item):
        if self.is_not_char(item):
            raise SILStringNotChar()

        self.string[index] = item.get_string()

    def __len__(self):
        return len(self.string)

    def __add__(self, b):
        return SILString(self.get_string() + b.get_string())

    def __eq__(self, b):
        return self.get_string() == b.get_string()

    def append(self, item):
        if self.is_not_char(item):
            raise SILStringNotChar()

        self.string.append(item.get_string())

    def pop(self, index):
        return SILString(self.string.pop(index))


class Expression(ErrorPacket):
    LITERAL = "lit"
    UNARY = "unary"
    BINARY_EXPRESSION = "bin_exp"
    VARIABLE = "var"
    INPUT = "input"
    CALL = "call"
    LIST_ACCESS = "list_access"

    def __init__(self, t, lvalue, rvalue, op):
        self.type = t
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.op = op


class Literal(Expression):
    def __init__(self, value):
        Expression.__init__(self, Expression.LITERAL, value, None, None)


class Call(Expression):
    def __init__(self, callee, args):
        Expression.__init__(self, Expression.CALL, None, None, None)
        self.callee = callee
        self.args = args


class Variable(Expression):
    def __init__(self, name):
        Expression.__init__(self, Expression.VARIABLE, name, None, None)


class ListAccess(Expression):
    def __init__(self, lst, index_expr):
        Expression.__init__(self, Expression.LIST_ACCESS, lst, index_expr, None)


class Unary(Expression):
    def __init__(self, unary_op, value):
        Expression.__init__(self, Expression.UNARY, value, None, unary_op)


class BinaryExpression(Expression):
    def __init__(self, lvalue, rvalue, op):
        Expression.__init__(self, Expression.BINARY_EXPRESSION, lvalue, rvalue, op)


class Input(Expression):
    def __init__(self, print):
        Expression.__init__(self, Expression.INPUT, print, None, None)


class Statement(ErrorPacket):
    PRINT = "print"
    FLAT = "flat"
    VAR_DECL = "var_decl"
    VAR_SET = "var_set"
    BLOCK = "block"
    IF = "if"
    WHILE = "while"
    FUNCTION = "function"
    RETURN = "return"
    STOP = "stop"
    SKIP = "skip"
    LIST_SET = "list_set"

    def __init__(self, t, expr):
        self.type = t
        self.expr = expr


class If(Statement):
    def __init__(self, expr: Expression, stmt: Statement, elseStmt: Statement):
        Statement.__init__(self, Statement.IF, expr)
        self.stmt = stmt
        self.elseStmt = elseStmt


class ExceptionStatment(Statement, Exception):
    pass


class Return(ExceptionStatment):
    def __init__(self, expr: Expression):
        Statement.__init__(self, Statement.RETURN, expr)


class Stop(ExceptionStatment):
    def __init__(self):
        Statement.__init__(self, Statement.STOP, None)


class Skip(ExceptionStatment):
    def __init__(self):
        Statement.__init__(self, Statement.SKIP, None)


class While(Statement):
    def __init__(self, expr: Expression, stmt: Statement, final_stmt: Statement | None = None):
        Statement.__init__(self, Statement.WHILE, expr)
        self.stmt = stmt
        self.final_stmt = final_stmt


class Block(Statement):
    def __init__(self, stmts):
        self.type = Statement.BLOCK
        self.stmts = stmts


class Function(Statement):
    def __init__(self, name: str, params: list[str], body: Block):
        Statement.__init__(self, Statement.FUNCTION, None)
        self.name = name
        self.params = params
        self.body = body
        self.param_count = len(params)


class VarDecl(Statement):
    def __init__(self, name, expr):
        Statement.__init__(self, Statement.VAR_DECL, expr)
        self.name = name


class VarSet(Statement):
    def __init__(self, name, expr):
        Statement.__init__(self, Statement.VAR_SET, expr)
        self.name = name


class ListSet(Statement):
    def __init__(self, lst, index_expr, expr):
        Statement.__init__(self, Statement.LIST_SET, expr)
        self.lst = lst
        self.index_expr = index_expr


class Callable:
    def call(self, tree_walker, args: list[Any], call: Call) -> Any:
        return None


class FunctionCallable(Callable):
    def __init__(self, func: Function):
        self.func = func
        self.param_count = func.param_count
        self.name = func.name

    def call(self, tree_walker, args: list[Expression], call: Call):
        env = Environment(tree_walker.env)
        for i, param in enumerate(self.func.params):
            env.declare_var(param, args[i])

        try:
            tree_walker.interpret_block(self.func.body, env)
        except Return as ret:
            return_value = tree_walker.eval_expr(ret.expr)
            tree_walker.env = env.parent
            return return_value

        return None
