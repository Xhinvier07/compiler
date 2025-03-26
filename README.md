# Vypr Programming Language

A simple programming language compiler that translates Vypr code (.vy files) to Python.

## Project Structure

```
compiler/
│
├── bin/               # Executable scripts
│   ├── vypr.bat       # Windows batch script to run the compiler
│   └── vypr_compiler.py # Main compiler script
│
├── src/               # Source code
│   └── vypr/          # Vypr language compiler components
│       ├── lexer.py   # Lexical analyzer
│       ├── parser.py  # Syntax analyzer
│       ├── semantic_analyzer.py # Semantic analyzer
│       ├── ir_generator.py     # Intermediate code generator
│       ├── code_generator.py   # Python code generator
│       └── compiler.py        # Main compiler class
│
├── examples/          # Example Vypr programs
│   ├── test_verbose.vy
│   ├── test_dot_concat.vy
│   └── fixed.vy
│
├── tests/             # Test files
│   └── test.py        # Basic compiler test
│
└── temp_py/           # Temporary Python output files
```

## Usage

To compile and run a Vypr program:

```bash
# From the root directory of the project
bin/vypr.bat examples/test_verbose.vy
```

### Command-line Options

- `-keep`: Keep the generated Python file instead of deleting it after execution
- `-verbose`: Show compilation progress and details
- `-o filename`: Specify output Python file name
- `-debug`: Show debug information including tokens

Example with options:
```bash
bin/vypr.bat examples/test_verbose.vy -keep -verbose
``` 