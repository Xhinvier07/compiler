from ir_generator import LabelIR, BinaryOpIR, UnaryOpIR, AssignIR, JumpIR, ConditionalJumpIR, CallIR, ReturnIR, PrintIR, InputIR


class CodeGenerator:
    def __init__(self, ir_functions):
        self.ir_functions = ir_functions
        self.output = []
    
    def generate_python_code(self):
        self.output.append("# Generated Python code")
        self.output.append("")
        
        # Add runtime support functions
        self.add_runtime_support()
        
        # Generate code for each function
        for func_name, func in self.ir_functions.items():
            self.generate_function(func)
        
        # Add main function call
        if "main" in self.ir_functions:
            self.output.append("")
            self.output.append("if __name__ == '__main__':")
            self.output.append("    main()")
        
        return "\n".join(self.output)
    
    def add_runtime_support(self):
        # Add any runtime support functions needed
        pass
    
    def generate_function(self, func):
        # Function header
        self.output.append(f"def {func.name}({', '.join(func.params)}):")
        
        # If function is empty, add pass statement
        if not func.instructions:
            self.output.append("    pass")
            return
        
        # Track variable declarations
        variables = set()
        for param in func.params:
            variables.add(param)
        
        # Temporary variables
        temp_vars = set()
        
        # Labels
        labels = {}
        i = 0
        for instr in func.instructions:
            if isinstance(instr, LabelIR):
                labels[instr.name] = i
            else:
                i += 1
        
        # Generate code for instructions
        i = 0
        indent_level = 1
        while i < len(func.instructions):
            instr = func.instructions[i]
            
            # Skip label definitions, they're handled in control flow
            if isinstance(instr, LabelIR):
                i += 1
                continue
            
            indent = "    " * indent_level
            
            if isinstance(instr, BinaryOpIR):
                if instr.dest.startswith("t"):
                    temp_vars.add(instr.dest)
                self.output.append(f"{indent}{instr.dest} = {instr.left} {instr.op} {instr.right}")
            
            elif isinstance(instr, UnaryOpIR):
                if instr.dest.startswith("t"):
                    temp_vars.add(instr.dest)
                self.output.append(f"{indent}{instr.dest} = {instr.op}{instr.operand}")
            
            elif isinstance(instr, AssignIR):
                if instr.dest not in variables and not instr.dest.startswith("t"):
                    variables.add(instr.dest)
                elif instr.dest.startswith("t"):
                    temp_vars.add(instr.dest)
                self.output.append(f"{indent}{instr.dest} = {instr.value}")
            
            elif isinstance(instr, JumpIR):
                self.output.append(f"{indent}# Jump to {instr.label}")
                # Find index for the target label
                goto_index = labels.get(instr.label, -1)
                if goto_index >= 0:
                    # We'll use a loop to simulate goto
                    i = goto_index - 1  # -1 because we'll increment i at the end of the loop
            
            elif isinstance(instr, ConditionalJumpIR):
                self.output.append(f"{indent}if {instr.condition}:")
                # True branch
                true_index = labels.get(instr.true_label, -1)
                if true_index >= 0:
                    self.output.append(f"{indent}    # Jump to {instr.true_label}")
                    i = true_index - 1  # -1 because we'll increment i at the end of the loop
                
                if instr.false_label:
                    self.output.append(f"{indent}else:")
                    # False branch
                    false_index = labels.get(instr.false_label, -1)
                    if false_index >= 0:
                        self.output.append(f"{indent}    # Jump to {instr.false_label}")
                        i = false_index - 1  # -1 because we'll increment i at the end of the loop
            
            elif isinstance(instr, CallIR):
                args_str = ", ".join(map(str, instr.args))
                if instr.dest:
                    if instr.dest.startswith("t"):
                        temp_vars.add(instr.dest)
                    self.output.append(f"{indent}{instr.dest} = {instr.function}({args_str})")
                else:
                    self.output.append(f"{indent}{instr.function}({args_str})")
            
            elif isinstance(instr, ReturnIR):
                if instr.value:
                    self.output.append(f"{indent}return {instr.value}")
                else:
                    self.output.append(f"{indent}return")
            
            elif isinstance(instr, PrintIR):
                self.output.append(f"{indent}print({instr.value})")
            
            elif isinstance(instr, InputIR):
                self.output.append(f"{indent}{instr.dest} = input()")
            
            i += 1
    
    def generate(self):
        return self.generate_python_code()