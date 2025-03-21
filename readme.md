# 🐍 Vypr Compiler

## 🎯 Overview
Vypr is a **lightweight** and **expressive** programming language designed to provide a **Python-like experience** 🐍 with a more **concise** and **structured** syntax.**✨** The goal of Vypr is to **simplify coding** by reducing syntactic overhead while maintaining **readability and flexibility**. 

Vypr's syntax is inspired by **Python**, but introduces its own set of **keywords, control structures, and functions**. Instead of executing code directly, Vypr **compiles into Python**, allowing for **seamless integration** with Python's ecosystem while offering an **alternative syntax** that some developers may find more intuitive. 🚀

### 🔄 Compilation Stages
🔹 **Lexical Analysis** - Converts source code into tokens.📜  
🔹 **Parsing** - Constructs an Abstract Syntax Tree (AST). 🌳  
🔹 **Semantic Analysis** - Ensures correctness by detecting undeclared variables. ✅  
🔹 **Intermediate Representation (IR)** - Translates AST into a structured format for easier code generation. 🔧  
🔹 **Code Generation** - Produces **Python code** that can be executed as a standalone script. 🏁

---
## ✨ Features
✅ **Lightweight Syntax** - Reduces boilerplate while maintaining clarity.  
✅ **Python-Compatible** - Generates Python code for execution.  
✅ **Structured Language** - Supports **variables, loops, conditionals, and functions**.  
✅ **Flexible Semantics** - Allows intuitive program flow with **indentation-based scoping**.  

---
## 📂 File Structure
📌 `lexer.py` - Tokenizes source code into tokens.  
📌 `parser.py` - Parses tokens into an AST.  
📌 `semantic_analyzer.py` - Performs semantic checks.  
📌 `ir_generator.py` - Converts AST into IR instructions.  
📌 `code_generator.py` - Generates Python code from IR.  
📌 `compiler.py` - Main compiler pipeline.  
📌 `test.py` - Example usage of the compiler.  

---
## 📝 Supported Syntax
### 🔹 Variable Declaration
```plaintext
var x = 10
var name = "Alice"
```

### 🔹 Conditional Statements
```plaintext
if x > 5:
    print "x is greater than 5"
else:
    print "x is 5 or less"
```

### 🔹 Loops
```plaintext
loop while x > 0:
    print x
    x = x - 1
```

### 🔹 Functions
```plaintext
func greet(name):
    print "Hello, " + name

greet("Alice")
```

---
## 🚀 Running the Compiler
To compile and generate Python code from a source program:
```python
from compiler import Compiler

source_code = """
var sum = 5 + 3
print sum  // Outputs: 8
"""

compiler = Compiler()
output_code = compiler.compile(source_code, "output.py")
print(output_code)
```

---
## 🏆 Output
This will generate a **Python file** (`output.py`) that executes the equivalent program in Python. 🖥️

---
## 📜 License
This project is **open-source**. Feel free to **modify and improve** it! 🌍💡
