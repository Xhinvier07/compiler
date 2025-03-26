from compiler import Compiler

# Initialize the compiler
compiler = Compiler()

# Compile source code
source_code = """

func calculateArea(length, width):
    return length * width

var area = calculateArea(5, 3)
print "The area is: " + area

"""

# Compile to Python
output = compiler.compile(source_code, "output.py")