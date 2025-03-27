import re
from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    VAR = auto()
    IF = auto()
    ELSE = auto()
    LOOP = auto()
    WHILE = auto()
    TIMES = auto()
    IN = auto()
    FUNC = auto()
    RETURN = auto()
    PRINT = auto()
    INPUT = auto()
    
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    CONCAT = auto()  # Now using ^ for concatenation
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    
    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()  # Used exclusively for property access
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    
    # Add array tokens
    LBRACKET = auto()
    RBRACKET = auto()

class Token:
    def __init__(self, token_type, value=None, line=0, column=0):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"
        return f"Token({self.type}, line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if len(self.text) > 0 else None
        self.indent_stack = [0]
        
        # Keywords mapping
        self.keywords = {
            'var': TokenType.VAR,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'loop': TokenType.LOOP,
            'while': TokenType.WHILE,
            'times': TokenType.TIMES,
            'in': TokenType.IN,
            'func': TokenType.FUNC,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT,
            'input': TokenType.INPUT,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN
        }
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.column += 1
    
    def peek(self, n=1):
        peek_pos = self.pos + n
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            # Skip to the end of the line
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
    
    def number(self):
        result = ''
        start_column = self.column
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.' and self.peek() and self.peek().isdigit():
            result += self.current_char
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            
            return Token(TokenType.FLOAT, float(result), self.line, start_column)
        
        return Token(TokenType.INTEGER, int(result), self.line, start_column)
    
    def string(self):
        result = ''
        start_column = self.column
        quote_char = self.current_char  # Save the quote character (' or ")
        self.advance()  # Skip the opening quote
        
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\' and self.peek() == quote_char:
                self.advance()  # Skip the backslash
            result += self.current_char
            self.advance()
        
        if self.current_char == quote_char:
            self.advance()  # Skip the closing quote
            return Token(TokenType.STRING, result, self.line, start_column)
        else:
            raise Exception(f"Unterminated string at line {self.line}, column {start_column}")
    
    def identifier(self):
        result = ''
        start_column = self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)
        
        # Special handling for boolean literals
        if token_type == TokenType.BOOLEAN:
            return Token(token_type, result == 'true', self.line, start_column)
        
        return Token(token_type, result, self.line, start_column)
    
    def process_indentation(self, indent_level):
        current_indent = self.indent_stack[-1]
        
        print(f"DEBUG: Processing indentation - level: {indent_level}, current: {current_indent}")
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            print(f"DEBUG: Pushed indent level {indent_level} to stack")
            return Token(TokenType.INDENT, indent_level, self.line, 1)
        
        tokens = []
        
        while indent_level < current_indent:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, self.line, 1))
            current_indent = self.indent_stack[-1]
            print(f"DEBUG: Popped indent level, new current: {current_indent}")
        
        if indent_level != current_indent:
            print(f"ERROR: Inconsistent indentation at line {self.line}: {indent_level} vs expected {current_indent}")
            raise Exception(f"Indentation error at line {self.line}: inconsistent indentation level")
        
        return tokens if tokens else None
    
    def get_next_token(self):
        while self.current_char is not None:
            # Handle indentation when at the beginning of a new line
            if self.column == 1 and self.current_char != '\n':
                indent_level = 0
                # Standardize indentation: count spaces and convert tabs to spaces
                while self.current_char in [' ', '\t']:
                    # Count tab as 4 spaces for indentation consistency
                    if self.current_char == '\t':
                        indent_level += 4
                    else:
                        indent_level += 1
                    self.advance()
                
                indentation_tokens = self.process_indentation(indent_level)
                if indentation_tokens:
                    if isinstance(indentation_tokens, list):
                        # Return the first token and store the rest for later
                        return indentation_tokens[0]
                    return indentation_tokens
            
            # Skip whitespace
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue
            
            # Comments
            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            # Newline
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
                self.advance()

                # Skip consecutive newlines (optional)
                while self.current_char == '\n':
                    self.line += 1
                    self.advance()

                return Token(TokenType.NEWLINE, '\n', self.line - 1, self.column)

            # Numbers
            if self.current_char.isdigit():
                return self.number()
            
            # Strings
            if self.current_char in ['"', "'"]:
                return self.string()
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Operators and punctuation
            if self.current_char == '+':
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '-':
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '*':
                token = Token(TokenType.MULTIPLY, '*', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '/':
                token = Token(TokenType.DIVIDE, '/', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '=':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, start_column)
                return Token(TokenType.ASSIGN, '=', self.line, start_column)
            
            if self.current_char == '!':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, start_column)
                raise Exception(f"Invalid token '!' at line {self.line}, column {start_column}")
            
            if self.current_char == '<':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, start_column)
                return Token(TokenType.LESS_THAN, '<', self.line, start_column)
            
            if self.current_char == '>':
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, start_column)
                return Token(TokenType.GREATER_THAN, '>', self.line, start_column)
            
            if self.current_char == '(':
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ')':
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ',':
                token = Token(TokenType.COMMA, ',', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ':':
                token = Token(TokenType.COLON, ':', self.line, self.column)
                self.advance()
                return token
            
            # Handle the dot token
            if self.current_char == '.':
                token = Token(TokenType.DOT, '.', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '^':
                token = Token(TokenType.CONCAT, '^', self.line, self.column)
                self.advance()
                return token
            
            # If we get here, we have an invalid character
            raise Exception(f"Invalid character '{self.current_char}' at line {self.line}, column {self.column}")

        # Generate dedent tokens at the end of the file
        if self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            return Token(TokenType.DEDENT, None, self.line, self.column)
        
        # EOF
        return Token(TokenType.EOF, None, self.line, self.column)

    def tokenize(self):
        tokens = []
        current_indent = 0
        indent_stack = [0]
        
        # Track the line number for indentation tracking
        line_num = 1
        line_start = True  # Flag to indicate if we're at the start of a line
        
        # Store the last non-whitespace token type
        last_non_whitespace_token_type = None
        
        while self.current_char is not None:
            # Skip whitespace, except for newlines
            if self.current_char.isspace() and self.current_char != '\n':
                if line_start:
                    # Count indentation at the beginning of a line
                    indent = 0
                    while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
                        if self.current_char == '\t':
                            indent += 4  # Count tab as 4 spaces
                        else:
                            indent += 1
                        self.advance()
                    
                    # Process indentation change
                    if indent > indent_stack[-1]:
                        # Increased indentation
                        indent_stack.append(indent)
                        print(f"DEBUG LEXER: Adding INDENT token at line {line_num}, indent level {indent}")
                        tokens.append(Token(TokenType.INDENT, indent, line_num, 1))
                    elif indent < indent_stack[-1]:
                        # Decreased indentation - may need multiple DEDENT tokens
                        while indent < indent_stack[-1]:
                            indent_stack.pop()
                            print(f"DEBUG LEXER: Adding DEDENT token at line {line_num}, indent level now {indent_stack[-1]}")
                            tokens.append(Token(TokenType.DEDENT, None, line_num, 1))
                        
                        # Check for invalid indentation
                        if indent != indent_stack[-1]:
                            print(f"ERROR LEXER: Inconsistent indentation at line {line_num}, got {indent} expected {indent_stack[-1]}")
                            raise Exception(f"Inconsistent indentation at line {line_num}")
                    
                    # No longer at start of line
                    line_start = False
                    # Re-check current character since we've advanced
                    continue
                else:
                    # Not at line start, skip the whitespace
                    self.skip_whitespace()
                continue
            
            # Handle comments
            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment()
                continue
            
            # Handle newlines (which also affect indentation)
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
                self.advance()
                
                # Skip consecutive newlines, but count each one
                while self.current_char == '\n':
                    self.line += 1
                    self.advance()
                
                # Add the NEWLINE token
                tokens.append(Token(TokenType.NEWLINE, '\n', line_num, self.column))
                line_num = self.line
                
                # Next token will be at the start of a line
                line_start = True
                continue
            
            # After processing indentation and newlines, we're no longer at line start
            line_start = False
            
            # Process other tokens
            if self.current_char.isdigit():
                tokens.append(self.number())
                last_non_whitespace_token_type = TokenType.INTEGER
            elif self.current_char in ['"', "'"]:
                tokens.append(self.string())
                last_non_whitespace_token_type = TokenType.STRING
            elif self.current_char.isalpha() or self.current_char == '_':
                token = self.identifier()
                tokens.append(token)
                last_non_whitespace_token_type = token.type
            elif self.current_char == '+':
                # Use PLUS for both arithmetic and string concatenation
                tokens.append(Token(TokenType.PLUS, '+', line_num, self.column))
                last_non_whitespace_token_type = TokenType.PLUS
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TokenType.MINUS, '-', line_num, self.column))
                last_non_whitespace_token_type = TokenType.MINUS
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.MULTIPLY, '*', line_num, self.column))
                last_non_whitespace_token_type = TokenType.MULTIPLY
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TokenType.DIVIDE, '/', line_num, self.column))
                last_non_whitespace_token_type = TokenType.DIVIDE
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TokenType.DOT, '.', line_num, self.column))
                last_non_whitespace_token_type = TokenType.DOT
                self.advance()
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.EQUAL, '==', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.EQUAL
                    self.advance()
                else:
                    tokens.append(Token(TokenType.ASSIGN, '=', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.ASSIGN
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.NOT_EQUAL, '!=', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.NOT_EQUAL
                    self.advance()
                else:
                    raise Exception(f"Invalid character '!' at line {line_num}, column {self.column}")
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.LESS_EQUAL, '<=', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.LESS_EQUAL
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LESS_THAN, '<', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.LESS_THAN
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token(TokenType.GREATER_EQUAL, '>=', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.GREATER_EQUAL
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GREATER_THAN, '>', line_num, self.column-1))
                    last_non_whitespace_token_type = TokenType.GREATER_THAN
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', line_num, self.column))
                last_non_whitespace_token_type = TokenType.LPAREN
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', line_num, self.column))
                last_non_whitespace_token_type = TokenType.RPAREN
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', line_num, self.column))
                last_non_whitespace_token_type = TokenType.COMMA
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TokenType.COLON, ':', line_num, self.column))
                last_non_whitespace_token_type = TokenType.COLON
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', line_num, self.column))
                last_non_whitespace_token_type = TokenType.LBRACKET
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', line_num, self.column))
                last_non_whitespace_token_type = TokenType.RBRACKET
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TokenType.CONCAT, '^', line_num, self.column))
                last_non_whitespace_token_type = TokenType.CONCAT
                self.advance()
            else:
                raise Exception(f"Invalid character '{self.current_char}' at line {line_num}, column {self.column}")
        
        # Add DEDENT tokens for any open indentation levels
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, line_num, self.column))
        
        # Ensure the token list ends with a NEWLINE token before EOF
        # This fixes the issue when files don't end with a newline
        if tokens and tokens[-1].type != TokenType.NEWLINE:
            # Make sure we're not inserting a newline after certain tokens 
            # that naturally appear at the end of statements
            if last_non_whitespace_token_type not in [TokenType.DEDENT, TokenType.NEWLINE]:
                print(f"DEBUG: Adding missing NEWLINE token at end of file")
                tokens.append(Token(TokenType.NEWLINE, None, line_num, self.column))
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, None, line_num, self.column))
        
        return tokens
    
    