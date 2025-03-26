from .ir_generator import LabelIR, BinaryOpIR, UnaryOpIR, AssignIR, JumpIR, ConditionalJumpIR, CallIR, ReturnIR, PrintIR, InputIR, ForLoopStartIR, ForLoopEndIR


class CodeGenerator:
    def __init__(self, ir_functions):
        self.ir_functions = ir_functions
        self.output = []
    
    def generate_python_code(self):
        # Fix: Completely re-implement the code generation to avoid comment leak
        
        # Header comment is isolated and will be first line in output
        header = "# Generated Python code"
        
        # Main function detection
        has_main = "main" in self.ir_functions
        
        # Create a list to store parts of the output
        parts = []
        
        # Add the header
        parts.append(header)
        parts.append("")  # Empty line after header
        
        # Add runtime support functions if needed
        runtime_funcs = self.add_runtime_support()
        if runtime_funcs:
            parts.append(runtime_funcs)
            parts.append("")  # Blank line after runtime functions
        
        # Process all non-main functions
        for func_name, func in self.ir_functions.items():
            if func_name != "main":
                # Process each function
                func_code = []
                # Function header
                func_code.append(f"def {func.name}({', '.join(func.params)}):")
                
                if not func.instructions:
                    func_code.append("    pass")
                else:
                    self._generate_function_body(func, func_code)
                
                # Add function to parts with blank line after
                parts.append("\n".join(func_code))
                parts.append("")  # Blank line between functions
        
        # Process main function last
        if has_main:
            main_func = self.ir_functions["main"]
            main_code = []
            main_code.append(f"def main():")
            
            if not main_func.instructions:
                main_code.append("    pass")
            else:
                self._generate_function_body(main_func, main_code)
            
            # Add main function
            parts.append("\n".join(main_code))
            parts.append("")  # Blank line
            
            # Add main execution code
            parts.append("if __name__ == '__main__':")
            parts.append("    main()")
        
        # Join all parts with newlines
        return "\n".join(parts)
    
    def _generate_function_body(self, func, code_lines):
        """
        Generate the function body code and add to code_lines list.
        This helps keep the function generation logic separate.
        """
        # Track indent level properly
        indent_level = 1
        
        for instr in func.instructions:
            # Skip label definitions
            if isinstance(instr, LabelIR):
                continue
            
            # Get proper indentation
            indent = "    " * indent_level
            
            # Process different instruction types
            if isinstance(instr, BinaryOpIR):
                code_lines.append(f"{indent}{instr.dest} = {instr.left} {instr.op} {instr.right}")
            
            elif isinstance(instr, UnaryOpIR):
                code_lines.append(f"{indent}{instr.dest} = {instr.op}{instr.operand}")
            
            elif isinstance(instr, AssignIR):
                code_lines.append(f"{indent}{instr.dest} = {instr.value}")
            
            elif isinstance(instr, ReturnIR):
                if instr.value:
                    code_lines.append(f"{indent}return {instr.value}")
                else:
                    code_lines.append(f"{indent}return")
            
            elif isinstance(instr, CallIR):
                args_str = ", ".join(map(str, instr.args))
                if instr.dest:
                    code_lines.append(f"{indent}{instr.dest} = {instr.function}({args_str})")
                else:
                    code_lines.append(f"{indent}{instr.function}({args_str})")
            
            elif isinstance(instr, PrintIR):
                code_lines.append(f"{indent}print({instr.value})")
            
            elif isinstance(instr, ForLoopStartIR):
                code_lines.append(f"{indent}for {instr.var} in {instr.iterable}:")
                indent_level += 1
            
            elif isinstance(instr, ForLoopEndIR):
                indent_level -= 1
                # Make sure we don't go below 1 (function body indentation)
                indent_level = max(1, indent_level)
        
        # Add pass if no instructions were processed
        if len(code_lines) == 1:  # Only the function header was added
            code_lines.append(f"    pass")
    
    def generate_function_code(self, func):
        """This method is no longer used but kept for compatibility"""
        func_lines = []
        func_lines.append(f"def {func.name}({', '.join(func.params)}):")
        
        if not func.instructions:
            func_lines.append("    pass")
            return func_lines
        
        self._generate_function_body(func, func_lines)
        return func_lines
    
    def generate(self):
        return self.generate_python_code()

    def add_runtime_support(self):
        """Add any runtime support functions needed"""
        # Currently no runtime support functions are needed
        # Return None or a string with runtime functions code
        return None