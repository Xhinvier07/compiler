import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from vypr.compiler import Compiler

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