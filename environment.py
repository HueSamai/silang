from error import *


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variable_map = {}

    def declare_var(self, name, value):
        if name in self.variable_map:
            raise VarException()

        self.variable_map[name] = value

    def set_var(self, name, value):
        if name in self.variable_map:
            self.variable_map[name] = value
            return

        if self.parent is None:
            raise VarException()

        self.parent.set_var(name, value)

    def get_var(self, name):
        if name in self.variable_map:
            return self.variable_map[name]

        if self.parent is None:
            raise VarException()

        return self.parent.get_var(name)
