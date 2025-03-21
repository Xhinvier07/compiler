from lexer import TokenType

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
        # Create main function
        self.functions["main"] = FunctionIR("main", [])
        self.current_function = self.functions["main"]
        
        for statement in node.statements:
            self.visit(statement)
        
        return self.functions
    
    def visit_VarDeclaration(self, node):
        if node.initial_value:
            value = self.visit(node.initial_value)
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
        iterator = node.variable
        iterable = self.visit(node.iterable)

        start_label = self.new_label()
        end_label = self.new_label()

        self.add_instruction(LabelIR(start_label))

        condition = self.new_temp()
        self.add_instruction(BinaryOpIR("in", condition, iterator, iterable))
        self.add_instruction(ConditionalJumpIR(condition, start_label, end_label))

        for statement in node.body:
            self.visit(statement)

        self.add_instruction(JumpIR(start_label))
        self.add_instruction(LabelIR(end_label))
    
    def visit_FunctionDeclaration(self, node):
        # Save current function
        prev_function = self.current_function
        
        # Create new function
        self.functions[node.name] = FunctionIR(node.name, node.parameters)
        self.current_function = self.functions[node.name]
        
        # Generate function body
        for statement in node.body:
            self.visit(statement)
        
        # Add implicit return if needed
        last_instr = self.current_function.instructions[-1] if self.current_function.instructions else None
        if not isinstance(last_instr, ReturnIR):
            self.add_instruction(ReturnIR())
        
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
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!=",
            TokenType.LESS_THAN: "<",
            TokenType.GREATER_THAN: ">",
            TokenType.LESS_EQUAL: "<=",
            TokenType.GREATER_EQUAL: ">="
        }

        op = op_map.get(node.operator.type, str(node.operator.type))
        dest = self.new_temp()
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
    
    def generate(self, ast):
        return self.visit(ast)


