from compiler import Compiler

# Initialize the compiler
compiler = Compiler()

# Compile source code
source_code = """

var x = 5
var y = 10

print (x + y)
"""

# Compile to Python
output = compiler.compile(source_code, "output.py")