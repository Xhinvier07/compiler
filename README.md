# Vypr Programming Language

A simple programming language compiler that translates Vypr code (.vy files) to Python. Vypr offers a clean syntax inspired by Python but with some unique features for readability and simplicity.

## Project Structure

```
compiler/
│
├── bin/               # Executable scripts
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
├── temp_py/           # Temporary Python output files
│
└── vypr.bat           # Windows batch script to run the compiler
```

## Usage

### Running Vypr Programs on Windows

To compile and run a Vypr program in the Command Prompt:

```cmd
vypr.bat examples\test_verbose.vy
```

In PowerShell, you need to use the `.\` prefix with the full filename:

```powershell
.\vypr.bat examples\test_verbose.vy
```

### Command-line Options

- `-keep`: Keep the generated Python file instead of deleting it after execution
- `-verbose`: Show compilation progress and details
- `-o filename`: Specify output Python file name
- `-debug`: Show debug information including tokens

Example with options:
```powershell
.\vypr.bat examples\test_verbose.vy -keep -verbose
```

### Setting Up a Simplified Command (Optional)

To run Vypr code without typing the `.bat` extension, you can create an alias in your PowerShell profile:

1. Create/edit your PowerShell profile:
   ```powershell
   notepad $PROFILE
   ```

2. Add this line to your profile:
   ```powershell
   function vypr { .\vypr.bat $args }
   ```

3. Restart PowerShell or run:
   ```powershell
   . $PROFILE
   ```

This allows you to use a simpler command:
```powershell
vypr examples\test_verbose.vy
```

## Vypr Language Documentation

### Basic Syntax

Vypr uses a clean, Python-like syntax with some unique features:

#### Variable Declaration and Assignment

Variables are declared using the `var` keyword:

```
var name = "World"
var age = 25
var pi = 3.14
var isActive = true
```

#### Data Types

Vypr supports the following primitive data types:
- Strings: `"Hello"` or `'Hello'`
- Integers: `42`
- Floating Point: `3.14`
- Booleans: `true` or `false`
- Arrays: `[1, 2, 3]`

#### Operators

Arithmetic operators:
```
var a = 5 + 3    // Addition
var b = 5 - 3    // Subtraction
var c = 5 * 3    // Multiplication
var d = 5 / 3    // Division
```

String concatenation:
```
var greeting = "Hello, " + name + "!"
```

Comparison operators:
```
var isEqual = a == b
var isNotEqual = a != b
var isGreater = a > b
var isLess = a < b
var isGreaterOrEqual = a >= b
var isLessOrEqual = a <= b
```

#### Control Flow

If-else statements:

```
if age >= 18:
    print "You are an adult"
else:
    print "You are a minor"
```

#### Loops

For loops (iterating over items):

```
var numbers = [1, 2, 3, 4, 5]
loop num in numbers:
    print "Number: " + num
```

Times loops (repeat a specific number of times):

```
loop 5 times:
    print "Hello!"
```

While loops:

```
var count = 0
while count < 5:
    print "Count: " + count
    count = count + 1
```

#### Functions

Function declaration:

```
func greet(name):
    print "Hello, " + name + "!"

func add(a, b):
    return a + b
```

Function calls:

```
greet("World")
var result = add(3, 5)
print "Result: " + result
```

#### Input and Output

Printing to console:

```
print "Hello, World!"
```

Getting user input:

```
var name
input name
print "Hello, " + name
```

#### Arrays and Operations

Array creation:

```
var fruits = ["apple", "banana", "orange"]
```

Accessing array elements (0-based indexing):

```
var firstFruit = fruits[0]  // "apple"
```

### Complete Examples

#### Example 1: Basic Function and Calculation

```
func calculateArea(length, width):
    return length * width

var area = calculateArea(5, 3)
print "The area is: " + area
```

#### Example 2: Working with Arrays

```
func calculate_sum(numbers):
    var sum = 0
    loop num in numbers:
        sum = sum + num
    return sum

func calculate_average(numbers, n):
    var sum = calculate_sum(numbers)
    return sum / n

var data = [0.1, 0.2, 0.3, 0.4, 0.5]
var total = calculate_sum(data)
print "Sum of data is: " + total

var avg = calculate_average(data, 5)
print "Average of data is: " + avg
```

#### Example 3: User Input and Conditionals

```
var age
print "Please enter your age:"
input age

if age < 13:
    print "You are a child."
else:
    if age < 20:
        print "You are a teenager."
    else:
        if age < 65:
            print "You are an adult."
        else:
            print "You are a senior."
```

### Advanced Features

#### String Operations

String concatenation:

```
var firstName = "John"
var lastName = "Doe"
var fullName = firstName + " " + lastName
```

#### Array Methods

Get array length:

```
var fruits = ["apple", "banana", "orange"]
var count = fruits.length
print "Number of fruits: " + count
```

## Language Implementation Details

The Vypr compiler consists of several stages:

1. **Lexical Analysis**: The `lexer.py` module tokenizes the source code into tokens.
2. **Syntax Analysis**: The `parser.py` module builds an Abstract Syntax Tree (AST) from the tokens.
3. **Semantic Analysis**: The `semantic_analyzer.py` module checks for semantic errors.
4. **IR Generation**: The `ir_generator.py` module converts the AST to an Intermediate Representation (IR).
5. **Code Generation**: The `code_generator.py` module generates Python code from the IR.

### Extending Vypr

To add new features to the Vypr language, you'll need to modify the following components:

1. **Add new tokens**: Update the `TokenType` enum in `lexer.py` and tokenization logic.
2. **Add AST nodes**: Create new node classes in `parser.py` for new language constructs.
3. **Update parsing logic**: Modify the `Parser` class to handle the new syntax.
4. **Add semantic checks**: Update the `SemanticAnalyzer` class in `semantic_analyzer.py` to check new constructs.
5. **Add IR and code generation**: Update the `IRGenerator` and `CodeGenerator` classes to handle new features.

## Contributing

If you'd like to contribute to Vypr, feel free to submit a pull request with your changes.

## License

This project is licensed under the terms of the included LICENSE file. 