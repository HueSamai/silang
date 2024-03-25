from tree_components import *
from error import *
from _parser import *
from environment import *
from baselib import *
from typing import Any


def cast(x: Any):
    return x


class TreeWalker:

    def __init__(self):
        Error.stage = "Runtime"
        self.env = Environment()
        self.global_env = self.env
        # setup std lib
        for name in Base.funs:
            Base.funs[name].name = name
            self.global_env.declare_var(name, Base.funs[name]())

    def run(self, stmts):
        for stmt in stmts:
            try:
                self.interpret(stmt)
            except Return as ret:
                Error.report_packet("Use of 'return' outside of a function", ret)
                exit(1)
            except Skip as skip:
                Error.report_packet("Use of 'skip' outside of a loop", skip)
                exit(1)
            except Stop as stop:
                Error.report_packet("Use of 'stop' outside of a loop", stop)
                exit(1)
            except KeyboardInterrupt:
                Error.report_flat("Program was forcefully stopped")
                exit(1)
            except RecursionError:
                Error.report_flat("Recursion limit reached. idk where bucko")
                exit(1)
            except Exception as e:
                Error.report_flat(f"Unknown error: {e}")
                exit(1)

    def interpret(self, stmt: Statement):
        if stmt.type == Statement.PRINT:
            self.interpret_print(stmt)
            return

        if stmt.type == Statement.VAR_DECL:
            self.interpret_var_dec(cast(stmt))
            return

        if stmt.type == Statement.IF:
            self.interpret_if(cast(stmt))
            return

        if stmt.type == Statement.VAR_SET:
            self.interpret_var_set(cast(stmt))
            return

        if stmt.type == Statement.LIST_SET:
            self.interpret_list_set(cast(stmt))
            return

        if stmt.type == Statement.RETURN:
            self.interpret_return(cast(stmt))
            return

        if stmt.type == Statement.STOP:
            self.interpret_stop(cast(stmt))
            return

        if stmt.type == Statement.SKIP:
            self.interpret_skip(cast(stmt))
            return

        if stmt.type == Statement.BLOCK:
            self.interpret_block(cast(stmt))
            return

        if stmt.type == Statement.WHILE:
            self.interpret_while(cast(stmt))
            return

        if stmt.type == Statement.FUNCTION:
            self.interpret_function(cast(stmt))
            return

        if stmt.type == Statement.FLAT:
            return self.eval_expr(stmt.expr)

        Error.report_packet(f"Unimplemented statement type '{stmt}'", stmt)
        exit(1)

    def interpret_print(self, stmt: Statement):
        value = self.eval_expr(stmt.expr)
        print(Parser.get_value(value), end="")

    def interpret_if(self, stmt: If):
        value = self.eval_expr(stmt.expr)
        if self.to_bool(value):
            self.interpret(stmt.stmt)
        else:
            if stmt.elseStmt is not None:
                self.interpret(stmt.elseStmt)

    def interpret_return(self, stmt: Return):
        raise stmt

    def interpret_stop(self, stmt: Stop):
        raise stmt

    def interpret_skip(self, stmt: Skip):
        raise stmt

    def interpret_block(self, stmt: Block, env: Environment | None = None):
        if env is None:
            env = Environment(self.env)
        self.env = env

        error = None
        for substmt in stmt.stmts:
            try:
                self.interpret(substmt)
            except Stop as stop:
                error = stop
                break

        # we catch and raise the error again, to keep the scopes correct
        self.env = self.env.parent
        if error is not None:
            raise error

    def interpret_while(self, stmt: While):
        while self.to_bool(self.eval_expr(stmt.expr)):
            try:
                self.interpret(stmt.stmt)
            except Skip:
                pass
            except Stop:
                break
            if stmt.final_stmt is not None:
                self.interpret(stmt.final_stmt)

    def interpret_function(self, stmt: Function):
        try:
            self.global_env.declare_var(stmt.name, FunctionCallable(stmt))
        except(VarException):
            Error.report_packet(
                f"Tried to define a function with name '{stmt.name}', but such a variable already exists in the global scope.",
                stmt)
            exit(1)

    def interpret_var_dec(self, stmt: VarDecl):
        try:
            # cast here is just to remove error
            cast(self.env).declare_var(stmt.name, self.eval_expr(stmt.expr))
        except(VarException):
            Error.report_packet(f"Tried to declare variable '{stmt.name}' that already exists in the current scope",
                                stmt)
            exit(1)

    def interpret_var_set(self, stmt: VarSet):
        try:
            # cast here is also to remove error
            cast(self.env).set_var(stmt.name, self.eval_expr(stmt.expr))
        except(VarException):
            Error.report_packet(f"Tried to set variable '{stmt.name}' that doesn't exist in the current scope", stmt)
            exit(1)

    def is_list(self, x):
        return type(x) is list or type(x) is SILString

    def interpret_list_set(self, stmt: ListSet):
        lst = self.eval_expr(stmt.lst)
        if not self.is_list(lst):
            Error.report_packet(f"Trying to list set non-list type '{self.type_to_str(type(lst))}'", stmt)
            exit(1)
        index = self.eval_expr(stmt.index_expr)
        if type(index) is not float:
            Error.report_packet(f"Trying to index a list with non-number type '{self.type_to_str(type(index))}'",
                                stmt.index_expr)
            exit(1)
        index = int(index)
        if index >= len(lst):
            Error.report_packet(
                f"List index out of bounds. Tried to access item '{index}' from list of size '{len(lst)}'",
                stmt.index_expr)
            exit(1)
        try:
            lst[index] = self.eval_expr(stmt.expr)
        except SILStringNotChar:
            Error.report_packet("Attempt to set character in string to non character", stmt.expr)
            exit(1)

    def type_to_str(self, t):
        if t is type(None):
            return "novalue"

        if t is float:
            return "number"

        if t is SILString:
            return "string"

        if t is bool:
            return "boolean"

        if t is list:
            return "list"

        return str(t)

    def interpret_call(self, expr: Call):
        callee = self.eval_expr(expr.callee)
        if not issubclass(type(callee), Callable):
            Error.report_packet("Tried to call a non-callable expression", expr)

        arg_count = len(expr.args)
        if callee.param_count < arg_count:
            Error.report_packet(
                f"Too many arguments passed to function '{callee.name}'. Expected {callee.param_count} got {arg_count}",
                expr)
            exit(1)
        elif callee.param_count > arg_count:
            Error.report_packet(
                f"Too few arguments passed to function '{callee.name}'. Expected {callee.param_count} got {arg_count}",
                expr)
            exit(1)

        return callee.call(self, [self.eval_expr(arg) for arg in expr.args], expr)

    def to_bool(self, val):
        return (val == True and type(val) is bool) or (val is not None and type(val) is not bool)

    def eval_expr(self, expr: Expression) -> Any:
        if expr.type == Expression.LITERAL:
            if type(expr.lvalue) is list:
                return [self.eval_expr(item) for item in expr.lvalue]
            return expr.lvalue

        if expr.type == Expression.LIST_ACCESS:
            lst = self.eval_expr(expr.lvalue)
            if not self.is_list(lst):
                Error.report_packet(f"Tried to index a non-list type {self.type_to_str(type(lst))}", expr)
                exit(1)

            index = self.eval_expr(expr.rvalue)
            if type(index) is not float:
                Error.report_packet(f"Trying to index a list with non-number type '{self.type_to_str(type(index))}'",
                                    expr.rvalue)
                exit(1)

            index = int(index)
            if index >= len(lst):
                Error.report_packet(
                    f"List index out of bounds. Tried to access item '{index}' from list of size '{len(lst)}'",
                    expr.rvalue)
                exit(1)

            return lst[index]

        if expr.type == Expression.CALL:
            return self.interpret_call(cast(expr))

        if expr.type == Expression.INPUT:
            value = self.eval_expr(expr.lvalue)
            if type(value) is not SILString:
                Error.report_packet(
                    f"Tried to use a non-string value '{self.type_to_str(type(value))}' with 'input' expression",
                    expr.lvalue)
                exit(1)

            return SILString(input(value.get_string().encode('ascii', errors='replace').decode('ascii')))

        if expr.type == Expression.VARIABLE:
            try:
                return cast(self.env).get_var(expr.lvalue)
            except(VarException):
                Error.report_packet(f"Tried to get variable '{expr.lvalue}' that doesn't exist in the current scope",
                                    expr)
                exit(1)

        if expr.type == Expression.UNARY:
            value = self.eval_expr(expr.lvalue)

            if expr.op == "-":
                if type(value) is not float:
                    Error.report_packet("Attempt to invert a non numerical value", expr)
                    exit(1)
                return -value

            return not self.to_bool(value)

        if expr.type == Expression.BINARY_EXPRESSION:
            lvalue = self.eval_expr(expr.lvalue)

            if expr.op == "and":
                if self.to_bool(lvalue):
                    return self.to_bool(self.eval_expr(expr.rvalue))
                return False

            if expr.op == "or":
                if not self.to_bool(lvalue):
                    return self.to_bool(self.eval_expr(expr.rvalue))
                return True

            rvalue = self.eval_expr(expr.rvalue)

            if expr.op == "==":
                return lvalue == rvalue

            if expr.op == "!=":
                return lvalue != rvalue

            if type(lvalue) != type(rvalue):
                Error.report_packet("Invalid operation between two incompatible types " +
                                    f"{self.type_to_str(type(lvalue))} and {self.type_to_str(type(rvalue))}", expr)
                exit(1)

            t = type(lvalue)

            if t == bool or t == list:
                Error.report_packet(f"Invalid operation '{expr.op}' between two {self.type_to_str(t)}s", expr)
                exit(1)

            if expr.op == "+":
                return lvalue + rvalue

            if t == SILString:
                Error.report_packet(f"Invalid operation '{expr.op}' between two {self.type_to_str(SILString)}s", expr)
                exit(1)

            if expr.op == ">=":
                return lvalue >= rvalue

            if expr.op == "<=":
                return lvalue <= rvalue

            if expr.op == ">":
                return lvalue > rvalue

            if expr.op == "<":
                return lvalue < rvalue

            if expr.op == "-":
                return lvalue - rvalue

            if expr.op == "*":
                return lvalue * rvalue

            if expr.op == "/":
                return lvalue / rvalue
