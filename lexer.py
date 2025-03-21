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
    
    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

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
        
        if indent_level > current_indent:
            self.indent_stack.append(indent_level)
            return Token(TokenType.INDENT, indent_level, self.line, 1)
        
        tokens = []
        
        while indent_level < current_indent:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, self.line, 1))
            current_indent = self.indent_stack[-1]
        
        if indent_level != current_indent:
            raise Exception(f"Indentation error at line {self.line}")
        
        return tokens if tokens else None
    
    def get_next_token(self):
        while self.current_char is not None:
            # Handle indentation when at the beginning of a new line
            if self.column == 1 and self.current_char != '\n':
                indent_level = 0
                while self.current_char == ' ':
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
        token = self.get_next_token()
        
        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)  # Add EOF token
        return tokens
    
    