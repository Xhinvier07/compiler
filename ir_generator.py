from lexer import TokenType
from parser import ReturnStatement

class IRInstruction:
    pass

class LabelIR(IRInstruction):  # Make sure this is above IRGenerator
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}:"

class BinaryOpIR(IRInstruction):
    def __init__(self, op, dest, left, right):
        self.op = op
        self.dest = dest
        self.left = left
        self.right = right
    
    def __str__(self):
        return f"{self.dest} = {self.left} {self.op} {self.right}"

class UnaryOpIR(IRInstruction):
    def __init__(self, op, dest, operand):
        self.op = op
        self.dest = dest
        self.operand = operand
    
    def __str__(self):
        return f"{self.dest} = {self.op} {self.operand}"

class AssignIR(IRInstruction):
    def __init__(self, dest, value):
        self.dest = dest
        self.value = value
    
    def __str__(self):
        return f"{self.dest} = {self.value}"

class JumpIR(IRInstruction):
    def __init__(self, label):
        self.label = label
    
    def __str__(self):
        return f"JUMP {self.label}"

class ConditionalJumpIR(IRInstruction):
    def __init__(self, condition, true_label, false_label=None):
        self.condition = condition
        self.true_label = true_label
        self.false_label = false_label
    
    def __str__(self):
        if self.false_label:
            return f"IF {self.condition} THEN JUMP {self.true_label} ELSE JUMP {self.false_label}"
        return f"IF {self.condition} THEN JUMP {self.true_label}"


class CallIR(IRInstruction):
    def __init__(self, function, args, dest=None):
        self.function = function
        self.args = args
        self.dest = dest
    
    def __str__(self):
        if self.dest:
            return f"{self.dest} = CALL {self.function}({', '.join(map(str, self.args))})"
        return f"CALL {self.function}({', '.join(map(str, self.args))})"

class ReturnIR(IRInstruction):
    def __init__(self, value=None):
        self.value = value
    
    def __str__(self):
        if self.value:
            return f"RETURN {self.value}"
        return "RETURN"

class PrintIR(IRInstruction):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"PRINT {self.value}"

class InputIR(IRInstruction):
    def __init__(self, dest):
        self.dest = dest
    
    def __str__(self):
        return f"{self.dest} = INPUT"

class FunctionIR:
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.instructions = []
    
    def add_instruction(self, instruction):
        self.instructions.append(instruction)
    
    def __str__(self):
        result = [f"FUNCTION {self.name}({', '.join(self.params)})"]
        for instruction in self.instructions:
            result.append(f"  {instruction}")
        return "\n".join(result)

class IRGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.functions = {}
        self.current_function = None
    
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def add_instruction(self, instruction):
        self.current_function.add_instruction(instruction)
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")
    
    def visit_Program(self, node):
        # First, collect function declarations and separate them from other statements
        function_declarations = []
        main_statements = []
        
        for statement in node.statements:
            if hasattr(statement, '__class__') and statement.__class__.__name__ == 'FunctionDeclaration':
                function_declarations.append(statement)
            else:
                main_statements.append(statement)
        
        print(f"DEBUG: Found {len(function_declarations)} function declarations")
        print(f"DEBUG: Found {len(main_statements)} main statements")
        
        # Process function declarations first
        for func_decl in function_declarations:
            self.visit_FunctionDeclaration(func_decl)
        
        # Create main function and process main statements
        self.functions["main"] = FunctionIR("main", [])
        self.current_function = self.functions["main"]
        
        print(f"DEBUG: Processing main statements")
        for i, statement in enumerate(main_statements):
            print(f"DEBUG: Processing main statement {i}: {statement.__class__.__name__}")
            self.visit(statement)
        
        # Add implicit return if needed
        last_instr = self.current_function.instructions[-1] if self.current_function.instructions else None
        if not isinstance(last_instr, ReturnIR):
            self.add_instruction(ReturnIR())
        
        return self.functions
    
    def visit_VarDeclaration(self, node):
        print(f"DEBUG: Processing var declaration: {node.name}")
        if node.initial_value:
            value = self.visit(node.initial_value)
            print(f"DEBUG: Adding instruction: {node.name} = {value}")
            self.add_instruction(AssignIR(node.name, value))
    
    def visit_Assignment(self, node):
        value = self.visit(node.value)
        self.add_instruction(AssignIR(node.variable.name, value))
        return node.variable.name
    
    def visit_IfStatement(self, node):
        condition = self.visit(node.condition)
        true_label = self.new_label()
        end_label = self.new_label()
        
        if node.else_body:
            false_label = self.new_label()
            self.add_instruction(ConditionalJumpIR(condition, true_label, false_label))
            
            # True branch
            self.add_instruction(LabelIR(true_label))
            for statement in node.body:
                self.visit(statement)
            self.add_instruction(JumpIR(end_label))
            
            # False branch
            self.add_instruction(LabelIR(false_label))
            for statement in node.else_body:
                self.visit(statement)
        else:
            self.add_instruction(ConditionalJumpIR(condition, true_label))

            # True branch
            self.add_instruction(LabelIR(true_label))
            for statement in node.body:
                self.visit(statement)
        
        self.add_instruction(LabelIR(end_label))
    
    def visit_TimesLoop(self, node):
        # Generate counter variable
        counter = self.new_temp()
        self.add_instruction(AssignIR(counter, 0))
        
        # Generate labels
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Loop condition
        count_value = self.visit(node.count)
        self.add_instruction(LabelIR(start_label))
        condition = self.new_temp()
        self.add_instruction(BinaryOpIR("<", condition, counter, count_value))
        self.add_instruction(ConditionalJumpIR(condition, start_label, end_label))

        # Loop body
        for statement in node.body:
            self.visit(statement)
        
        # Increment counter
        self.add_instruction(BinaryOpIR("+", counter, counter, 1))
        self.add_instruction(JumpIR(start_label))
        
        # End of loop
        self.add_instruction(LabelIR(end_label))
    
    def visit_WhileLoop(self, node):
        # Generate labels
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Loop condition
        self.add_instruction(LabelIR(start_label))
        condition = self.visit(node.condition)
        self.add_instruction(ConditionalJumpIR(condition, start_label, end_label))

        
        # Loop body
        for statement in node.body:
            self.visit(statement)
        
        self.add_instruction(JumpIR(start_label))
        
        # End of loop
        self.add_instruction(LabelIR(end_label))

    def visit_ForLoop(self, node):
        # Get the iterable expression
        iterable = self.visit(node.iterable)
        
        # Generate unique variable name for the loop counter
        loop_var = node.variable
        
        # Use ForLoopStartIR and ForLoopEndIR for cleaner code generation
        self.add_instruction(ForLoopStartIR(loop_var, iterable))
        
        # Process the loop body
        for statement in node.body:
            self.visit(statement)
        
        # Add loop footer
        self.add_instruction(ForLoopEndIR())
    
    def visit_FunctionDeclaration(self, node):
        # Debug print
        print(f"DEBUG: Processing function: {node.name} with {len(node.body)} statements")
        for idx, stmt in enumerate(node.body):
            print(f"DEBUG:  Statement {idx}: {stmt.__class__.__name__}")
        
        # Save current function
        prev_function = self.current_function
        
        # Create new function
        self.functions[node.name] = FunctionIR(node.name, node.parameters)
        self.current_function = self.functions[node.name]
        
        # Generate function body - only include statements that were explicitly parsed as part of the function
        # The return statement is typically the last statement in a function
        for statement in node.body:
            # If we find a return statement, process it and then break
            # This ensures we don't include statements after the return
            self.visit(statement)
            if isinstance(statement, ReturnStatement):
                print(f"DEBUG: Found return statement, stopping function body")
                break
        
        # Add implicit return if needed
        last_instr = self.current_function.instructions[-1] if self.current_function.instructions else None
        if not isinstance(last_instr, ReturnIR):
            self.add_instruction(ReturnIR())
        
        # Debug print function instructions
        print(f"DEBUG: Function {node.name} has {len(self.current_function.instructions)} instructions")
        for idx, instr in enumerate(self.current_function.instructions):
            print(f"DEBUG:  Instruction {idx}: {instr}")
        
        # Restore previous function
        self.current_function = prev_function
    
    def visit_ReturnStatement(self, node):
        if node.value:
            value = self.visit(node.value)
            self.add_instruction(ReturnIR(value))
        else:
            self.add_instruction(ReturnIR())
    
    def visit_PrintStatement(self, node):
        value = self.visit(node.expression)
        # If the value is an array or other complex type, ensure it's printed correctly
        self.add_instruction(PrintIR(value))
    
    def visit_InputStatement(self, node):
        self.add_instruction(InputIR(node.variable))
    
    def visit_ExpressionStatement(self, node):
        self.visit(node.expression)

    def visit_BinaryOperation(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Map token types to operations
        op_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.MULTIPLY: "*",
            TokenType.DIVIDE: "/",
            TokenType.CONCAT: "+",  # Use + in Python, but with string conversion
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!=",
            TokenType.LESS_THAN: "<",
            TokenType.GREATER_THAN: ">",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER_EQUAL: ">="
        }

        op = op_map.get(node.operator.type, str(node.operator.type))
        dest = self.new_temp()
        
        # If this is string concatenation with the . operator
        if node.operator.type == TokenType.CONCAT:
            # Convert both operands to strings
            self.add_instruction(BinaryOpIR("+", dest, f"str({left})", f"str({right})"))
        else:
            # Regular binary operation
            self.add_instruction(BinaryOpIR(op, dest, left, right))
        
        return dest

    def visit_UnaryOperation(self, node):
        operand = self.visit(node.operand)
        
        # Map token types to operations
        op_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-"
        }
        
        op = op_map.get(node.operator.type, str(node.operator.type))
        dest = self.new_temp()
        self.add_instruction(UnaryOpIR(op, dest, operand))
        return dest
    
    def visit_Literal(self, node):
        # For string literals, add quotes
        if isinstance(node.value, str):
            return f'"{node.value}"'
        # For other literals, just return their value
        return node.value
    
    def visit_Identifier(self, node):
        # For identifiers, just return their name
        return node.name
    
    def visit_FunctionCall(self, node):
        args = [self.visit(arg) for arg in node.arguments]
        dest = self.new_temp()
        self.add_instruction(CallIR(node.function, args, dest))
        return dest
    
    def visit_ArrayLiteral(self, node):
        # Problem: This might be trying to join integers with strings
        elements = [self.visit(element) for element in node.elements]
        
        # Make sure all elements are properly handled as values, not joined as strings
        element_str = []
        for element in elements:
            # Ensure each element is properly processed
            element_str.append(str(element))
        
        # Return the array literal
        return f"[{', '.join(element_str)}]"
    
    def generate(self, ast):
        return self.visit(ast)

class ForLoopStartIR(IRInstruction):
    def __init__(self, var, iterable):
        self.var = var
        self.iterable = iterable
    
    def __str__(self):
        return f"FOR {self.var} IN {self.iterable}"

class ForLoopEndIR(IRInstruction):
    def __str__(self):
        return "END FOR"


