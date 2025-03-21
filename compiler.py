# Vypr Compiler

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGenerator
from code_generator import CodeGenerator

class Compiler:
    def __init__(self):
        pass
    
    def compile(self, source_code, output_filename=None):
        try:
            # Step 1: Lexical Analysis
            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            print("Lexical analysis completed successfully.")
            
            # Step 2: Syntax Analysis
            parser = Parser(tokens)
            ast = parser.parse()
            print("Syntax analysis completed successfully.")
            
            # Step 3: Semantic Analysis
            semantic_analyzer = SemanticAnalyzer()
            success, errors = semantic_analyzer.analyze(ast)
            
            if not success:
                print("Semantic analysis failed with errors:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print("Semantic analysis completed successfully.")
            
            # Step 4: Intermediate Code Generation
            ir_generator = IRGenerator()
            ir_functions = ir_generator.generate(ast)
            print("Intermediate code generation completed successfully.")
            
            # Step 5: Code Generation
            code_generator = CodeGenerator(ir_functions)
            output_code = code_generator.generate()
            print("Code generation completed successfully.")
            
            # Write output to file if specified
            if output_filename:
                with open(output_filename, 'w') as f:
                    f.write(output_code)
                print(f"Output written to {output_filename}")
            
            return output_code
        
        except Exception as e:
            print(f"Compilation error: {e}")
            return None

if __name__ == "__main__":
    compiler = Compiler()
