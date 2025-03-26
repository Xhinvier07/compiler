# Vypr Compiler

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from code_generator import CodeGenerator

class Compiler:
    def __init__(self):
        self.last_error = None
    
    def compile(self, source_code, output_filename=None, verbose=False):
        try:
            # Step 1: Lexical Analysis
            if verbose:
                print("\n" + "="*80)
                print(" "*30 + "PHASE 1: LEXICAL ANALYSIS" + " "*30)
                print("="*80)
                print("Starting lexical analysis...")
                print("Tokenizing source code...")
                
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            
            if verbose:
                print("\nTokens generated:")
                token_count = len(tokens)
                print(f"  Total tokens: {token_count}")
                token_types = {}
                for token in tokens:
                    if token.type in token_types:
                        token_types[token.type] += 1
                    else:
                        token_types[token.type] = 1
                print("  Token breakdown:")
                for token_type, count in token_types.items():
                    print(f"    {token_type}: {count}")
                print("\nLexical analysis completed successfully.")
                print("-"*80)
            else:
                print("Lexical analysis completed successfully.")
            
            # Step 2: Syntax Analysis
            if verbose:
                print("\n" + "="*80)
                print(" "*30 + "PHASE 2: SYNTAX ANALYSIS" + " "*30)
                print("="*80)
                print("Starting syntax analysis...")
                print("Building abstract syntax tree (AST)...")
            
            parser = Parser(tokens)
            try:
                ast = parser.parse()
                if verbose:
                    print("\nAST structure:")
                    
                    def count_nodes(node):
                        if hasattr(node, 'statements'):
                            print(f"  Program with {len(node.statements)} top-level statements")
                            
                            # Count statement types
                            stmt_types = {}
                            for stmt in node.statements:
                                stmt_type = stmt.__class__.__name__
                                if stmt_type in stmt_types:
                                    stmt_types[stmt_type] += 1
                                else:
                                    stmt_types[stmt_type] = 1
                            
                            print("  Statement types:")
                            for stmt_type, count in stmt_types.items():
                                print(f"    {stmt_type}: {count}")
                    
                    count_nodes(ast)
                    print("\nSyntax analysis completed successfully.")
                    print("-"*80)
                else:
                    print("Syntax analysis completed successfully.")
            except Exception as e:
                error_msg = str(e)
                # Add helpful hint for indentation errors
                if "Expected TokenType.INDENT" in error_msg or "Indentation error" in error_msg:
                    self.last_error = f"{error_msg}\nHint: Check your indentation. The compiler uses spaces for indentation (tabs are converted to 4 spaces)."
                else:
                    self.last_error = error_msg
                
                if verbose:
                    print("\nSyntax analysis failed:")
                    print(f"  Error: {self.last_error}")
                    print("-"*80)
                else:
                    print(f"Syntax analysis failed: {self.last_error}")
                
                return False
            
            # Step 3: Semantic Analysis
            if verbose:
                print("\n" + "="*80)
                print(" "*30 + "PHASE 3: SEMANTIC ANALYSIS" + " "*30)
                print("="*80)
                print("Starting semantic analysis...")
                print("Checking for semantic errors...")
            
            semantic_analyzer = SemanticAnalyzer()
            success, errors = semantic_analyzer.analyze(ast)
            
            if not success:
                self.last_error = f"Semantic analysis failed: {errors}"
                
                if verbose:
                    print("\nSemantic analysis failed with errors:")
                    for i, error in enumerate(errors, 1):
                        print(f"  Error {i}: {error}")
                    print("-"*80)
                else:
                    print("Semantic analysis failed with errors:")
                    for error in errors:
                        print(f"  - {error}")
                
                return False
            
            if verbose:
                print("\nSemantic checks passed.")
                print("No semantic errors found.")
                print("\nSemantic analysis completed successfully.")
                print("-"*80)
            else:
                print("Semantic analysis completed successfully.")
            
            # Step 4: Intermediate Code Generation
            if verbose:
                print("\n" + "="*80)
                print(" "*30 + "PHASE 4: IR GENERATION" + " "*30)
                print("="*80)
                print("Starting intermediate representation (IR) generation...")
                print("Converting AST to IR...")
            
            ir_generator = IRGenerator()
            ir_functions = ir_generator.generate(ast)
            
            if verbose:
                print("\nIR generation results:")
                print(f"  Functions generated: {len(ir_functions)}")
                for func_name, func in ir_functions.items():
                    instr_count = len(func.instructions)
                    print(f"  Function '{func_name}': {instr_count} instructions")
                
                print("\nIntermediate code generation completed successfully.")
                print("-"*80)
            else:
                print("Intermediate code generation completed successfully.")
            
            # Step 5: Code Generation
            if verbose:
                print("\n" + "="*80)
                print(" "*30 + "PHASE 5: CODE GENERATION" + " "*30)
                print("="*80)
                print("Starting Python code generation...")
                print("Converting IR to Python code...")
            
            code_generator = CodeGenerator(ir_functions)
            output_code = code_generator.generate()
            
            if verbose:
                if output_code:
                    lines = output_code.count('\n') + 1
                    print(f"\nGenerated Python code ({lines} lines).")
                    print("\nCode generation completed successfully.")
                    print("-"*80)
                else:
                    print("\nNo Python code was generated.")
                    print("-"*80)
            else:
                print("Code generation completed successfully.")
            
            # Write output to file if specified
            if output_filename:
                with open(output_filename, 'w') as f:
                    f.write(output_code)
                
                if verbose:
                    print(f"\nOutput successfully written to file: {output_filename}")
                else:
                    print(f"Output written to {output_filename}")
            
            return output_code
        
        except Exception as e:
            self.last_error = str(e)
            
            if verbose:
                print(f"\nCompilation error: {e}")
                print("-"*80)
            else:
                print(f"Compilation error: {e}")
            
            return None
    
    def get_last_error(self):
        return self.last_error

if __name__ == "__main__":
    compiler = Compiler()
