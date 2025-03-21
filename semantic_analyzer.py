from ir_generator import LabelIR, AssignIR, BinaryOpIR, UnaryOpIR, JumpIR, ConditionalJumpIR, CallIR, ReturnIR, PrintIR, InputIR

class SymbolTable:
    def __init__(self, enclosing_scope=None):
        self.symbols = {}
        self.enclosing_scope = enclosing_scope

    def define(self, name, type_=None):
        self.symbols[name] = type_

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]

        if self.enclosing_scope:
            return self.enclosing_scope.lookup(name)

        return None

    def resolve(self, name):
        if name in self.symbols:
            return True

        if self.enclosing_scope:
            return self.enclosing_scope.resolve(name)

        return False


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors = []

    def error(self, message, line=None, column=None):
        if line is not None and column is not None:
            message = f"{message} at line {line}, column {column}"
        self.errors.append(message)

    def enter_scope(self):
        self.current_scope = SymbolTable(enclosing_scope=self.current_scope)

    def exit_scope(self):
        self.current_scope = self.current_scope.enclosing_scope

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        if hasattr(node, 'children'):
            for child in node.children:
                self.visit(child)

    def visit_Program(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDeclaration(self, node):
        if self.current_scope.resolve(node.name):
            self.error(f"Variable '{node.name}' already declared")
        else:
            # Set initial type to None, will be determined by initial value
            self.current_scope.define(node.name)

            if node.initial_value:
                self.visit(node.initial_value)

    def visit_Assignment(self, node):
        if not self.current_scope.resolve(node.variable.name):
            self.error(f"Variable '{node.variable.name}' not declared")

        self.visit(node.value)

    def visit_IfStatement(self, node):
        self.visit(node.condition)

        self.enter_scope()
        for statement in node.body:
            self.visit(statement)
        self.exit_scope()

        if node.else_body:
            self.enter_scope()
            for statement in node.else_body:
                self.visit(statement)
            self.exit_scope()

    def visit_TimesLoop(self, node):
        self.visit(node.count)

        self.enter_scope()
        for statement in node.body:
            self.visit(statement)
        self.exit_scope()

    def visit_WhileLoop(self, node):
        self.visit(node.condition)

        self.enter_scope()
        for statement in node.body:
            self.visit(statement)
        self.exit_scope()

    def visit_ForLoop(self, node):
        self.visit(node.iterable)

        self.enter_scope()
        # Declare loop variable in the loop scope
        self.current_scope.define(node.variable)

        for statement in node.body:
            self.visit(statement)
        self.exit_scope()

    def visit_FunctionDeclaration(self, node):
        if self.current_scope.resolve(node.name):
            self.error(f"Function '{node.name}' already declared")
        else:
            # Store function info in symbol table
            self.current_scope.define(node.name, {'type': 'function', 'params': node.parameters})

            # Create new scope for function body
            self.enter_scope()

            # Add parameters to function scope
            for param in node.parameters:
                self.current_scope.define(param)

            # Visit function body
            for statement in node.body:
                self.visit(statement)

            self.exit_scope()

    def visit_ReturnStatement(self, node):
        if node.value:
            self.visit(node.value)

    def visit_PrintStatement(self, node):
        self.visit(node.expression)

    def visit_InputStatement(self, node):
        if not self.current_scope.resolve(node.variable):
            self.error(f"Variable '{node.variable}' not declared")

    def visit_ExpressionStatement(self, node):
        self.visit(node.expression)

    def visit_BinaryOperation(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOperation(self, node):
        self.visit(node.operand)

    def visit_Literal(self, node):
        # Nothing to do for literals
        pass

    def visit_Identifier(self, node):
        if not self.current_scope.resolve(node.name):
            self.error(f"Variable '{node.name}' not declared")

    def visit_FunctionCall(self, node):
        # Check if function exists
        func_info = self.current_scope.lookup(node.function)

        if not func_info or func_info.get('type') != 'function':
            self.error(f"Function '{node.function}' not declared")
        else:
            # Check argument count
            expected_params = func_info.get('params', [])
            if len(expected_params) != len(node.arguments):
                self.error(
                    f"Function '{node.function}' expects {len(expected_params)} arguments, got {len(node.arguments)}")

            # Visit arguments
            for arg in node.arguments:
                self.visit(arg)

    def analyze(self, ast):
        self.visit(ast)
        return len(self.errors) == 0, self.errors