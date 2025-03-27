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
        
        # Create label/instruction position mapping
        label_positions = {}
        for i, instr in enumerate(func.instructions):
            if isinstance(instr, LabelIR):
                label_positions[instr.name] = i
        
        i = 0
        while i < len(func.instructions):
            instr = func.instructions[i]
            
            # Get proper indentation
            indent = "    " * indent_level
            
            # Process labels (for jumps and conditional jumps)
            if isinstance(instr, LabelIR):
                i += 1
                continue
            
            # Handle conditional jumps (if statements)
            if isinstance(instr, ConditionalJumpIR):
                if instr.false_label:  # if-else structure
                    # This is a full if-else with true and false branches
                    true_pos = label_positions.get(instr.true_label)
                    false_pos = label_positions.get(instr.false_label)
                    
                    if true_pos is not None and false_pos is not None:
                        # Find the end label by looking for a jump at the end of the true block
                        end_label = None
                        for j in range(false_pos - 1, true_pos, -1):
                            if isinstance(func.instructions[j], JumpIR):
                                end_label = func.instructions[j].label
                                break
                        
                        # Write the if condition
                        code_lines.append(f"{indent}if {instr.condition}:")
                        indent_level += 1
                        
                        # Process the true branch (skip the label at the start)
                        j = true_pos + 1  # Skip the label
                        while j < len(func.instructions) and j < false_pos:
                            # Skip jump to end label - it's implicit in Python
                            if isinstance(func.instructions[j], JumpIR) and func.instructions[j].label == end_label:
                                j += 1
                                continue
                                
                            inner_instr = func.instructions[j]
                            # Special case: handle nested conditional jumps in the true branch
                            if isinstance(inner_instr, ConditionalJumpIR):
                                # Recursively process the nested if
                                nested_indent = "    " * indent_level
                                self._process_nested_if(inner_instr, func, code_lines, indent_level, label_positions)
                                j = self._find_next_instruction_after_nested_if(j, func.instructions, label_positions)
                            # Don't recursively handle more jumps - just the immediate code
                            elif not isinstance(inner_instr, (JumpIR, LabelIR)):
                                new_indent_level = self._process_single_instruction(inner_instr, code_lines, indent_level)
                                indent_level = new_indent_level
                            j += 1
                        
                        # End of true block, back to if level to add else
                        indent_level -= 1
                        
                        # Add the else clause
                        code_lines.append(f"{indent}else:")
                        indent_level += 1
                        
                        # Process the false branch (skip the label at the start)
                        end_pos = len(func.instructions)
                        if end_label and end_label in label_positions:
                            end_pos = label_positions[end_label]
                            
                        j = false_pos + 1  # Skip the label
                        while j < end_pos:
                            inner_instr = func.instructions[j]
                            # Special case: handle nested conditional jumps in the else branch
                            if isinstance(inner_instr, ConditionalJumpIR):
                                # Recursively process the nested if
                                nested_indent = "    " * indent_level
                                self._process_nested_if(inner_instr, func, code_lines, indent_level, label_positions)
                                j = self._find_next_instruction_after_nested_if(j, func.instructions, label_positions)
                            # Don't recursively handle more jumps - just the immediate code
                            elif not isinstance(inner_instr, (JumpIR, LabelIR)):
                                new_indent_level = self._process_single_instruction(inner_instr, code_lines, indent_level)
                                indent_level = new_indent_level
                            j += 1
                        
                        # Back to normal indent level
                        indent_level -= 1
                        
                        # Skip ahead in processing to after the end label
                        i = end_pos + 1
                        continue
                else:  # if-only structure without an else
                    # This is just an if without an else
                    true_pos = label_positions.get(instr.true_label)
                    if true_pos is not None:
                        # Find the end - all instructions until the next label
                        end_pos = len(func.instructions)
                        for j in range(true_pos + 1, len(func.instructions)):
                            if isinstance(func.instructions[j], LabelIR) and func.instructions[j].name != instr.true_label:
                                end_pos = j
                                break
                        
                        # Write the if condition
                        code_lines.append(f"{indent}if {instr.condition}:")
                        indent_level += 1
                        
                        # Process the true branch
                        j = true_pos + 1  # Skip the label
                        while j < end_pos:
                            inner_instr = func.instructions[j]
                            # Don't handle more jumps - just the immediate code
                            if not isinstance(inner_instr, (JumpIR, ConditionalJumpIR, LabelIR)):
                                new_indent_level = self._process_single_instruction(inner_instr, code_lines, indent_level)
                                indent_level = new_indent_level
                            j += 1
                        
                        # Back to normal indent level
                        indent_level -= 1
                        
                        # Skip ahead in processing
                        i = end_pos
                        continue
            
            # Handle unconditional jumps (loop back, etc.)
            elif isinstance(instr, JumpIR):
                # Skip for now - loops will handle their own jumps
                i += 1
                continue
                
            # Process regular instructions
            elif not isinstance(instr, (LabelIR, JumpIR, ConditionalJumpIR)):
                new_indent_level = self._process_single_instruction(instr, code_lines, indent_level)
                indent_level = new_indent_level
            
            i += 1
        
        # Add pass if no instructions were processed
        if len(code_lines) == 1:  # Only the function header was added
            code_lines.append(f"    pass")
    
    def _process_single_instruction(self, instr, code_lines, indent_level):
        """Process a single non-jump instruction and add it to code_lines"""
        indent = "    " * indent_level
        
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
        
        elif isinstance(instr, InputIR):
            code_lines.append(f"{indent}{instr.dest} = input()")
        
        elif isinstance(instr, ForLoopStartIR):
            code_lines.append(f"{indent}for {instr.var} in {instr.iterable}:")
            indent_level += 1
        
        elif isinstance(instr, ForLoopEndIR):
            indent_level -= 1
            # Make sure we don't go below 1
            indent_level = max(1, indent_level)
        
        return indent_level
    
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

    def _process_nested_if(self, instr, func, code_lines, indent_level, label_positions):
        """Process a nested if statement and add to code_lines"""
        indent = "    " * indent_level
        
        if instr.false_label:  # nested if-else structure
            true_pos = label_positions.get(instr.true_label)
            false_pos = label_positions.get(instr.false_label)
            
            if true_pos is not None and false_pos is not None:
                # Find the end label
                end_label = None
                for j in range(false_pos - 1, true_pos, -1):
                    if isinstance(func.instructions[j], JumpIR):
                        end_label = func.instructions[j].label
                        break
                
                # Write the if condition
                code_lines.append(f"{indent}if {instr.condition}:")
                
                # Process the true branch with increased indent
                new_indent_level = indent_level + 1
                j = true_pos + 1  # Skip the label
                while j < false_pos:
                    # Skip jumps to end
                    if isinstance(func.instructions[j], JumpIR) and func.instructions[j].label == end_label:
                        j += 1
                        continue
                    
                    inner_instr = func.instructions[j]
                    # Handle nested ifs recursively
                    if isinstance(inner_instr, ConditionalJumpIR):
                        self._process_nested_if(inner_instr, func, code_lines, new_indent_level, label_positions)
                        j = self._find_next_instruction_after_nested_if(j, func.instructions, label_positions)
                    elif not isinstance(inner_instr, (JumpIR, LabelIR)):
                        # Add the instruction with proper indentation
                        self._format_instruction(inner_instr, code_lines, "    " * new_indent_level)
                        j += 1
                    else:
                        j += 1
                
                # Write the else clause
                code_lines.append(f"{indent}else:")
                
                # Process the false branch with increased indent
                j = false_pos + 1  # Skip the label
                end_pos = len(func.instructions)
                if end_label and end_label in label_positions:
                    end_pos = label_positions[end_label]
                
                while j < end_pos:
                    inner_instr = func.instructions[j]
                    # Handle nested ifs recursively in the else branch
                    if isinstance(inner_instr, ConditionalJumpIR):
                        self._process_nested_if(inner_instr, func, code_lines, new_indent_level, label_positions)
                        j = self._find_next_instruction_after_nested_if(j, func.instructions, label_positions)
                    elif not isinstance(inner_instr, (JumpIR, LabelIR)):
                        # Add the instruction with proper indentation
                        self._format_instruction(inner_instr, code_lines, "    " * new_indent_level)
                        j += 1
                    else:
                        j += 1
    
    def _format_instruction(self, instr, code_lines, indent):
        """Format a single instruction with proper indentation"""
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
        elif isinstance(instr, InputIR):
            code_lines.append(f"{indent}{instr.dest} = input()")
    
    def _find_next_instruction_after_nested_if(self, curr_pos, instructions, label_positions):
        """Find the next instruction position after a nested if structure"""
        # Start from the current conditional jump
        if not isinstance(instructions[curr_pos], ConditionalJumpIR):
            return curr_pos + 1
        
        cond_jump = instructions[curr_pos]
        
        # If this is an if-else, find the end label
        if cond_jump.false_label:
            true_pos = label_positions.get(cond_jump.true_label)
            false_pos = label_positions.get(cond_jump.false_label)
            
            if true_pos is not None and false_pos is not None:
                # Find the end label
                end_label = None
                for j in range(false_pos - 1, true_pos, -1):
                    if isinstance(instructions[j], JumpIR):
                        end_label = instructions[j].label
                        break
                
                # Find the position of the end label
                if end_label and end_label in label_positions:
                    return label_positions[end_label] + 1
        
        # If we couldn't determine the end, just return the next position
        return curr_pos + 1