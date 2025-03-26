from lexer import TokenType, Token

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Statement(ASTNode):
    pass

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class VarDeclaration(Statement):
    def __init__(self, name, initial_value=None):
        self.name = name
        self.initial_value = initial_value

class Assignment(Statement):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

class IfStatement(Statement):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class LoopStatement(Statement):
    pass

class TimesLoop(LoopStatement):
    def __init__(self, count, body):
        self.count = count
        self.body = body

class WhileLoop(LoopStatement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop(LoopStatement):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class FunctionDeclaration(Statement):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

class ReturnStatement(Statement):
    def __init__(self, value=None):
        self.value = value

class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class InputStatement(Statement):
    def __init__(self, variable):
        self.variable = variable

class Expression(ASTNode):
    pass

class BinaryOperation(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOperation(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class Literal(Expression):
    def __init__(self, value, type_):
        self.value = value
        self.type = type_

class Identifier(Expression):
    def __init__(self, name):
        self.name = name

class FunctionCall(Expression):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class ArrayLiteral(Expression):
    def __init__(self, elements):
        self.elements = elements

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]
    
    def error(self, message):
        token = self.current_token
        raise Exception(f"{message} at line {token.line}, column {token.column}")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            return
        self.error(f"Expected {token_type}, got {self.current_token.type}")
    
    def peek(self, n=1):
        peek_pos = self.pos + n
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def program(self):
        """program : statement_list"""
        statements = self.statement_list()
        return Program(statements)

    def statement_list(self):
        """statement_list : (statement NEWLINE)*"""
        statements = []

        # Skip leading newlines
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        while self.current_token.type != TokenType.EOF:
            # Stop if we encounter a DEDENT token, which indicates the end of a block
            if self.current_token.type == TokenType.DEDENT:
                break
                
            # Process the statement
            statements.append(self.statement())

            # Ensure that statements are separated by newlines
            while self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)

        return statements

    def statement(self):
        """
        statement : var_declaration
                  | assignment
                  | if_statement
                  | loop_statement
                  | function_declaration
                  | return_statement
                  | print_statement
                  | input_statement
                  | expression_statement
        """
        if self.current_token.type == TokenType.VAR:
            return self.var_declaration()
        elif self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.LOOP:
            return self.loop_statement()
        elif self.current_token.type == TokenType.FUNC:
            return self.function_declaration()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.print_statement()
        elif self.current_token.type == TokenType.INPUT:
            return self.input_statement()
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Could be assignment or function call
            if self.peek().type == TokenType.ASSIGN:
                return self.assignment()
            else:
                return self.expression_statement()
        elif self.current_token.type == TokenType.DEDENT:
            # Skip DEDENT tokens at the statement level
            self.eat(TokenType.DEDENT)
            # Try to get the next statement recursively
            return self.statement()

        # If no valid statement, raise an error
        self.error(f"Unexpected token in statement: {self.current_token}")

    def eat_newline_or_eof(self):
        """Utility method to eat a newline token or handle EOF gracefully"""
        if self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
        elif self.current_token.type == TokenType.EOF:
            # End of file reached without newline, that's okay
            # We don't advance the token pointer as that would go past EOF
            print(f"DEBUG: End of file reached without newline after statement")
            pass
        elif self.current_token.type == TokenType.DEDENT:
            # DEDENT token is also acceptable at the end of a statement
            print(f"DEBUG: DEDENT token found after statement, consuming it")
            self.eat(TokenType.DEDENT)
        else:
            self.error(f"Expected newline, EOF, or DEDENT, got {self.current_token.type}")
    
    def var_declaration(self):
        """var_declaration : VAR IDENTIFIER (ASSIGN expression)? NEWLINE"""
        self.eat(TokenType.VAR)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        initial_value = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            initial_value = self.expression()

        self.eat_newline_or_eof()
        return VarDeclaration(name, initial_value)
    
    def assignment(self):
        """assignment : IDENTIFIER ASSIGN expression NEWLINE"""
        variable = Identifier(self.current_token.value)
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.expression()
        self.eat_newline_or_eof()
        return Assignment(variable, value)
    
    def if_statement(self):
        """
        if_statement : IF expression COLON NEWLINE INDENT statement_list DEDENT
                     (ELSE COLON NEWLINE INDENT statement_list DEDENT)?
        """
        self.eat(TokenType.IF)
        condition = self.expression()
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        self.eat(TokenType.INDENT)
        
        body = []
        while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            body.append(self.statement())
        
        self.eat(TokenType.DEDENT)
        
        else_body = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.COLON)
            self.eat(TokenType.NEWLINE)
            self.eat(TokenType.INDENT)
            
            else_body = []
            while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                else_body.append(self.statement())
            
            self.eat(TokenType.DEDENT)
        
        return IfStatement(condition, body, else_body)
    
    def loop_statement(self):
        """
        loop_statement : times_loop
                      | while_loop
                      | for_loop
        """
        if self.current_token.type == TokenType.LOOP:
            if self.peek().type == TokenType.IDENTIFIER and self.peek(2).type == TokenType.IN:
                return self.for_loop()
            elif self.peek(2).type == TokenType.TIMES:
                return self.times_loop()
            else:
                self.error("Invalid loop statement")
        elif self.current_token.type == TokenType.WHILE:
            self.eat(TokenType.WHILE)
            condition = self.expression()
            self.eat(TokenType.COLON)
            self.eat(TokenType.NEWLINE)
            self.eat(TokenType.INDENT)
            
            body = []
            while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                body.append(self.statement())
            
            self.eat(TokenType.DEDENT)
            return WhileLoop(condition, body)
        else:
            self.error("Invalid loop statement")
    
    def times_loop(self):
        """
        times_loop : LOOP expression TIMES COLON NEWLINE INDENT statement_list DEDENT
        """
        self.eat(TokenType.LOOP)
        count = self.expression()
        self.eat(TokenType.TIMES)
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        
        # Make INDENT optional to handle files with tabs or inconsistent indentation
        if self.current_token.type == TokenType.INDENT:
            self.eat(TokenType.INDENT)
        else:
            print(f"Warning: Expected indentation after loop declaration at line {self.current_token.line}")
        
        body = []
        # Process statements until we encounter a dedent or tokens that might indicate end of loop
        loop_end_tokens = [TokenType.DEDENT, TokenType.EOF, TokenType.VAR, TokenType.FUNC]
        
        while self.current_token.type not in loop_end_tokens:
            # Skip unexpected tokens - more lenient parsing
            if self.current_token.type in (TokenType.INDENT, TokenType.NEWLINE):
                self.eat(self.current_token.type)
                continue
                
            body.append(self.statement())
        
        # Make DEDENT optional
        if self.current_token.type == TokenType.DEDENT:
            self.eat(TokenType.DEDENT)
        
        return TimesLoop(count, body)
    
    def function_declaration(self):
        """
        function_declaration : FUNC IDENTIFIER LPAREN parameter_list? RPAREN COLON 
                              NEWLINE INDENT statement_list DEDENT
        parameter_list : IDENTIFIER (COMMA IDENTIFIER)*
        """
        print(f"DEBUG: Parsing function declaration at line {self.current_token.line}")
        
        self.eat(TokenType.FUNC)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        print(f"DEBUG: Function name: {name}")
        
        self.eat(TokenType.LPAREN)
        
        parameters = []
        if self.current_token.type == TokenType.IDENTIFIER:
            param_name = self.current_token.value
            parameters.append(param_name)
            print(f"DEBUG: Parameter: {param_name}")
            self.eat(TokenType.IDENTIFIER)
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                param_name = self.current_token.value
                parameters.append(param_name)
                print(f"DEBUG: Parameter: {param_name}")
                self.eat(TokenType.IDENTIFIER)
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        
        # Try to find INDENT token, but be lenient if it's missing
        expected_indented = False
        if self.current_token.type == TokenType.INDENT:
            print(f"DEBUG: Found explicit INDENT token")
            self.eat(TokenType.INDENT)
            expected_indented = True
        else:
            print(f"DEBUG: No explicit INDENT token found, assuming implicit indentation for function body")
        
        body = []
        
        # Process statements until we hit a token that suggests we're back at the top level
        # or detect dedentation
        top_level_tokens = [TokenType.DEDENT, TokenType.FUNC, TokenType.EOF]
        
        # If we already have a var declaration, this is likely part of the function body
        # because we've already consumed the NEWLINE after the function declaration
        if self.current_token.type == TokenType.VAR:
            print(f"DEBUG: First statement appears to be a variable declaration, assuming it's part of function body")
        
        # Continue parsing until we find a return statement or hit a dedent
        has_return = False
        
        while self.current_token.type not in top_level_tokens:
            # Skip any unexpected indentation tokens within function
            if self.current_token.type in [TokenType.INDENT, TokenType.NEWLINE]:
                print(f"DEBUG: Skipping token {self.current_token.type}")
                self.eat(self.current_token.type)
                continue
            
            print(f"DEBUG: Parsing statement in function body, token: {self.current_token.type}")
            statement = self.statement()
            body.append(statement)
            print(f"DEBUG: Added statement to function body: {statement.__class__.__name__}")
            
            # If the current statement was a return, we've reached the end of the function
            if isinstance(statement, ReturnStatement):
                print(f"DEBUG: Found return statement, ending function body")
                has_return = True
                break
            
            # If we've hit something that looks like it's outside the function, stop
            if self.current_token.type in top_level_tokens:
                print(f"DEBUG: Found token suggesting end of function: {self.current_token.type}")
                break
        
        # Consume DEDENT token if present
        if self.current_token.type == TokenType.DEDENT and expected_indented:
            print(f"DEBUG: Found DEDENT token, consuming it")
            self.eat(TokenType.DEDENT)
        
        # If there's no return statement and no DEDENT, assume the function ends after the last statement
        if not has_return and self.current_token.type not in top_level_tokens:
            print(f"DEBUG: No return statement found, assuming function ends here")
        
        print(f"DEBUG: Finished parsing function, body has {len(body)} statements")
        return FunctionDeclaration(name, parameters, body)
    
    def return_statement(self):
        """return_statement : RETURN expression? NEWLINE"""
        self.eat(TokenType.RETURN)
        
        value = None
        if self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
            value = self.expression()
        
        self.eat_newline_or_eof()
        return ReturnStatement(value)
    
    def print_statement(self):
        """print_statement : PRINT expression NEWLINE"""
        self.eat(TokenType.PRINT)
        expression = self.expression()
        self.eat_newline_or_eof()
        return PrintStatement(expression)
    
    def input_statement(self):
        """input_statement : INPUT IDENTIFIER NEWLINE"""
        self.eat(TokenType.INPUT)
        variable = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat_newline_or_eof()
        return InputStatement(variable)

    def expression_statement(self):
        """expression_statement : expression NEWLINE"""
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)  # Skip multiple newlines

        expression = self.expression()

        self.eat_newline_or_eof()  # Ensure at least one newline after expression (or EOF)
        return ExpressionStatement(expression)
    
    def expression(self):
        """expression : logical_expression"""
        return self.logical_expression()
    
    def logical_expression(self):
        """
        logical_expression : comparison_expression ((AND | OR) comparison_expression)*
        """
        # Note: AND and OR not implemented in the lexer yet
        return self.comparison_expression()
    
    def comparison_expression(self):
        """
        comparison_expression : arithmetic_expression ((==|!=|<|>|<=|>=) arithmetic_expression)*
        """
        node = self.arithmetic_expression()
        
        while self.current_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL, 
                                          TokenType.LESS_THAN, TokenType.GREATER_THAN,
                                          TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.current_token
            self.eat(self.current_token.type)
            right = self.arithmetic_expression()
            node = BinaryOperation(node, operator, right)
        
        return node
    
    def arithmetic_expression(self):
        """
        arithmetic_expression : term ((PLUS | MINUS | CONCAT) term)*
        """
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.CONCAT):
            operator = self.current_token
            self.eat(self.current_token.type)
            right = self.term()
            node = BinaryOperation(node, operator, right)
        
        return node
    
    def term(self):
        """
        term : factor ((MULTIPLY | DIVIDE) factor)*
        """
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.current_token
            self.eat(self.current_token.type)
            right = self.factor()
            node = BinaryOperation(node, operator, right)
        
        return node

    def factor(self):
        """
        factor : (PLUS | MINUS) factor
               | INTEGER
               | FLOAT
               | STRING
               | BOOLEAN
               | LPAREN expression RPAREN
               | array_literal
               | function_call
               | IDENTIFIER
        """
        # Skip any unexpected newlines
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)

        token = self.current_token

        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOperation(token, self.factor())

        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOperation(token, self.factor())

        elif token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Literal(token.value, "integer")

        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return Literal(token.value, "float")

        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return Literal(token.value, "string")

        elif token.type == TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            return Literal(token.value, "boolean")

        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node

        elif token.type == TokenType.LBRACKET:
            return self.array_literal()

        elif token.type == TokenType.IDENTIFIER:
            # Check if it's a function call
            if self.peek().type == TokenType.LPAREN:
                return self.function_call()
            else:
                self.eat(TokenType.IDENTIFIER)
                return Identifier(token.value)

        self.error(f"Invalid factor: {token}")
    
    def function_call(self):
        """
        function_call : IDENTIFIER LPAREN argument_list? RPAREN
        argument_list : expression (COMMA expression)*
        """
        function_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        
        arguments = []
        if self.current_token.type != TokenType.RPAREN:
            arguments.append(self.expression())
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                arguments.append(self.expression())
        
        self.eat(TokenType.RPAREN)
        return FunctionCall(function_name, arguments)

    def array_literal(self):
        """array_literal : LBRACKET (expression (COMMA expression)*)? RBRACKET"""
        self.eat(TokenType.LBRACKET)
        
        elements = []
        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.expression())
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                elements.append(self.expression())
        
        self.eat(TokenType.RBRACKET)
        return ArrayLiteral(elements)

    def for_loop(self):
        """
        for_loop : LOOP IDENTIFIER IN expression COLON NEWLINE INDENT statement_list DEDENT
        """
        self.eat(TokenType.LOOP)
        variable = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.IN)
        iterable = self.expression()
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        
        # Make INDENT optional to handle files with tabs or inconsistent indentation
        if self.current_token.type == TokenType.INDENT:
            self.eat(TokenType.INDENT)
        else:
            print(f"Warning: Expected indentation after for loop declaration at line {self.current_token.line}")
        
        body = []
        # Process statements until we encounter a dedent or tokens that might indicate end of loop
        loop_end_tokens = [TokenType.DEDENT, TokenType.EOF, TokenType.VAR, TokenType.FUNC]
        
        while self.current_token.type not in loop_end_tokens:
            # Skip unexpected tokens - more lenient parsing
            if self.current_token.type in (TokenType.INDENT, TokenType.NEWLINE):
                self.eat(self.current_token.type)
                continue
                
            body.append(self.statement())
        
        # Make DEDENT optional
        if self.current_token.type == TokenType.DEDENT:
            self.eat(TokenType.DEDENT)
        
        return ForLoop(variable, iterable, body)

    def parse(self):
        return self.program()