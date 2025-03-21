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

        # If no valid statement, raise an error
        self.error(f"Unexpected token in statement: {self.current_token}")

    def var_declaration(self):
        """var_declaration : VAR IDENTIFIER (ASSIGN expression)? NEWLINE"""
        self.eat(TokenType.VAR)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        initial_value = None
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            initial_value = self.expression()

        self.eat(TokenType.NEWLINE)
        return VarDeclaration(name, initial_value)
    
    def assignment(self):
        """assignment : IDENTIFIER ASSIGN expression NEWLINE"""
        variable = Identifier(self.current_token.value)
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.expression()
        self.eat(TokenType.NEWLINE)
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
        loop_statement : times_loop | while_loop | for_loop
        times_loop : LOOP expression TIMES COLON NEWLINE INDENT statement_list DEDENT
        while_loop : LOOP WHILE expression COLON NEWLINE INDENT statement_list DEDENT
        for_loop : LOOP IDENTIFIER IN expression COLON NEWLINE INDENT statement_list DEDENT
        """
        self.eat(TokenType.LOOP)
        
        # Times loop
        if self.peek().type == TokenType.TIMES:
            count = self.expression()
            self.eat(TokenType.TIMES)
            self.eat(TokenType.COLON)
            self.eat(TokenType.NEWLINE)
            self.eat(TokenType.INDENT)
            
            body = []
            while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                body.append(self.statement())
            
            self.eat(TokenType.DEDENT)
            return TimesLoop(count, body)
        
        # While loop
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
        
        # For loop
        else:
            variable = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.IN)
            iterable = self.expression()
            self.eat(TokenType.COLON)
            self.eat(TokenType.NEWLINE)
            self.eat(TokenType.INDENT)
            
            body = []
            while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
                body.append(self.statement())
            
            self.eat(TokenType.DEDENT)
            return ForLoop(variable, iterable, body)
    
    def function_declaration(self):
        """
        function_declaration : FUNC IDENTIFIER LPAREN parameter_list? RPAREN COLON 
                              NEWLINE INDENT statement_list DEDENT
        parameter_list : IDENTIFIER (COMMA IDENTIFIER)*
        """
        self.eat(TokenType.FUNC)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        
        parameters = []
        if self.current_token.type == TokenType.IDENTIFIER:
            parameters.append(self.current_token.value)
            self.eat(TokenType.IDENTIFIER)
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                parameters.append(self.current_token.value)
                self.eat(TokenType.IDENTIFIER)
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        self.eat(TokenType.INDENT)
        
        body = []
        while self.current_token.type not in (TokenType.DEDENT, TokenType.EOF):
            body.append(self.statement())
        
        self.eat(TokenType.DEDENT)
        return FunctionDeclaration(name, parameters, body)
    
    def return_statement(self):
        """return_statement : RETURN expression? NEWLINE"""
        self.eat(TokenType.RETURN)
        
        value = None
        if self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
            value = self.expression()
        
        self.eat(TokenType.NEWLINE)
        return ReturnStatement(value)
    
    def print_statement(self):
        """print_statement : PRINT expression NEWLINE"""
        self.eat(TokenType.PRINT)
        expression = self.expression()
        self.eat(TokenType.NEWLINE)
        return PrintStatement(expression)
    
    def input_statement(self):
        """input_statement : INPUT IDENTIFIER NEWLINE"""
        self.eat(TokenType.INPUT)
        variable = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.NEWLINE)
        return InputStatement(variable)

    def expression_statement(self):
        """expression_statement : expression NEWLINE"""
        while self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)  # Skip multiple newlines

        expression = self.expression()

        self.eat(TokenType.NEWLINE)  # Ensure at least one newline after expression
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
        arithmetic_expression : term ((PLUS | MINUS) term)*
        """
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
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

    def parse(self):
        return self.program()