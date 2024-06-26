from tree_components import *
import os
import random
import sys


class Num(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) is not SILString:
            return None
        try:
            return float(args[0].get_string())
        except ValueError:
            return None


class Length(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        expr = args[0]
        try:
            return float(len(expr))
        except:
            Error.report_packet(f"Tried to get length of a non-list type '{tree_walker.type_to_str(type(expr))}'",
                                call.args[0])
            exit(1)


class Push(Callable):

    def __init__(self):
        self.param_count = 2

    def call(self, tree_walker, args, call: Call):
        lst = args[0]
        expr = args[1]

        if not tree_walker.is_list(lst):
            Error.report_packet(f"Tried to push to a non-list type '{tree_walker.type_to_str(type(lst))}'",
                                call.args[0])
            exit(1)

        try:
            lst.append(expr)
        except SILStringNotChar:
            Error.report_packet("Tried to push a non-character onto a string", call.args[1])
            exit(1)


class Pop(Callable):

    def __init__(self):
        self.param_count = 2

    def call(self, tree_walker, args, call):
        lst = args[0]
        index = args[1]
        if not tree_walker.is_list(lst):
            Error.report_packet(f"Tried to pop from a non-list type '{tree_walker.type_to_str(type(lst))}'",
                                call.args[0])
            exit(1)
        if type(index) is not float:
            Error.report_packet(f"Cannot pop with non-numeric index of type '{tree_walker.type_to_str(type(lst))}'",
                                call.args[1])
            exit(1)

        index = int(index)

        if index >= len(lst):
            Error.report_packet(f"Index out of bounds! Cannot pop item '{index}' from list of size '{len(lst)}'",
                                call.args[1])
            exit(1)

        return lst.pop(int(index))


class Read(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) is not SILString:
            Error.report_packet("First argument of 'read' must be the path to a file as a string", call.args[0])
            exit(1)

        try:
            file = open(args[0].get_string(), "r")
        except FileNotFoundError:
            Error.report_packet(f"File '{args[0].get_string()}' couldn't be found", call.args[0])
            exit(1)

        contents = file.read()
        file.close()
        return SILString(contents)


class Write(Callable):
    def __init__(self):
        self.param_count = 2

    def call(self, tree_walker, args, call):
        if type(args[0]) is not SILString:
            Error.report_packet("First argument of 'write' must be the path to a file as a string", call.args[0])
            exit(1)

        if type(args[1]) is not SILString:
            Error.report_packet("Second argument of 'write' must be a string of the new contents of the file",
                                call.args[0])
            exit(1)

        file = open(args[0].get_string(), "wb")
        file.write(bytes([ord(x) for x in args[1].get_string()]))
        file.close()


class Exists(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) is not SILString:
            Error.report_packet("First argument of 'exists' must be the path to a file as a string", call.args[0])
            exit(1)

        return os.path.isfile(args[0].get_string())


class Random(Callable):
    def __init__(self):
        self.param_count = 0

    def call(self, tree_walker, args, call):
        return float(random.random())


class Seed(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        random.seed(args[0].get_string() if type(args[0]) is SILString else args[0])


class Round(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        try:
            return float(round(args[0]))
        except TypeError:
            return None


class Exit(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) != float:
            Error.report_packet(f"First argument of 'exit' must be type {tree_walker.type_to_str(float)}", call.args[0])
            exit(1)

        exit(int(args[0]))


class Arg(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) != float:
            Error.report_packet(f"First argument of 'arg' must be type {tree_walker.type_to_str(float)}", call.args[0])
            exit(1)

        try:
            return sys.argv[int(args[0]) + 1]
        except IndexError:
            return None


class Type(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) == float:
            return SILString("number")

        if type(args[0]) == SILString:
            return SILString("string")

        if type(args[0]) == list:
            return SILString("list")

        if type(args[0]) == bool:
            return SILString("bool")
        
        if issubclass(type(args[0]), Callable):
            return SILString("function")

        if args[0] == None:
            return None


class Char(Callable):
    def __init__(self):
        self.param_count = 1

    def call(self, tree_walker, args, call):
        if type(args[0]) == SILString:
            if len(args[0]) != 1:
                Error.report_packet(f"Non-character string was passed to 'char': '{args[0]}'", call.args[0])
                exit(1)
            return float(ord(args[0].get_string()))

        elif type(args[0]) == float:
            return SILString(chr(int(args[0])))

        else:
            Error.report_packet(
                f"First argument of 'char' must either be of type '{tree_walker.type_to_str(float)}' or '{tree_walker.type_to_str(SILString)}'",
                call.args[0])
            exit(1)


# our exported functions
class Base:
    funs = {
        "num": Num,
        "length": Length,
        "push": Push,
        "pop": Pop,
        "read": Read,
        "write": Write,
        "exists": Exists,
        "rng": Random,
        "seed": Seed,
        "round": Round,
        "exit": Exit,
        "arg": Arg,
        "char": Char,
        "type": Type
    }
