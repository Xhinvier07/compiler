from compiler import Compiler

# Initialize the compiler
compiler = Compiler()

# Compile source code
source_code = """
var sum = 5 + 3
var name = "John"
print(sum)
print(name)

"""

# Compile to Python
output = compiler.compile(source_code, "output.py")