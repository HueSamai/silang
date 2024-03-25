from lexer import MultiFileLexer
from tokens import *
from error import *
from _parser import *
from tree_walker import *
import sys
import os

input_file_path = sys.argv[1]
if not os.path.exists(input_file_path):
    Error.report_flat(f"File '{input_file_path}' not found")
    exit(1)

tokens = MultiFileLexer(input_file_path).tokens

t = ""
for token in tokens:
    t += f"{token.type} {token.lexeme}\n"

with open("out.txt", "wb") as file:
    file.write(t.encode('ascii', errors='replace'))

if Error.error_occurred:
    exit(1)

parser = Parser(tokens)

stmts = parser.parse()

if Error.error_occurred:
    exit(1)

# print(Parser.tree_to_str(parser.parse()))

walker = TreeWalker()
walker.run(stmts)
