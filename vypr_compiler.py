#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import traceback
from compiler import Compiler

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Vypr Language Compiler')
    parser.add_argument('input_file', help='The .vy file to compile')
    parser.add_argument('-o', '--output', help='Specify output Python file name')
    parser.add_argument('-keep', action='store_true', help='Keep the generated Python file')
    parser.add_argument('-verbose', action='store_true', help='Show compilation progress')
    parser.add_argument('-debug', action='store_true', help='Show debug information including tokens')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if input file exists and has .vy extension
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    if not args.input_file.endswith('.vy'):
        print(f"Error: Input file must have .vy extension.")
        sys.exit(1)
    
    # Create temp_py directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_py')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        output_file = os.path.join(temp_dir, f"{base_name}.py")
    
    # Read the source code
    try:
        with open(args.input_file, 'r') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Initialize and run the compiler
    compiler = Compiler()
    
    # If in debug mode, dump tokens
    if args.debug:
        from lexer import Lexer
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        print("=== TOKENS ===")
        for token in tokens:
            print(token)
        print("=== END TOKENS ===")
    
    try:
        # Capture and redirect compiler output if not verbose
        if not args.verbose and not args.debug:
            original_print = print
            
            def filtered_print(*args, **kwargs):
                pass  # Suppress output
            
            # Override print function during compilation
            import builtins
            builtins.print = filtered_print
        
        # Compile the code
        result = compiler.compile(source_code, output_file)
        
        # Restore original print function if it was overridden
        if not args.verbose and not args.debug:
            builtins.print = original_print
        
        if not result:
            print(f"Compilation failed: {compiler.get_last_error()}")
            sys.exit(1)
        
        # Run the compiled Python file
        try:
            print(f"Running compiled code from {output_file}...")
            print("\n" + "="*60 + "\n" + " "*20 + "PROGRAM OUTPUT" + " "*20 + "\n" + "="*60 + "\n")
            
            subprocess.run([sys.executable, output_file], check=True)
            
            print("\n" + "="*60 + "\n" + " "*20 + "END OUTPUT" + " "*22 + "\n" + "="*60)
            print("\nExecution completed.")
        except subprocess.CalledProcessError as e:
            print("\n" + "="*60)
            print(f"Error executing compiled code: {e}")
            print("="*60)
        
        # Delete the output file unless -keep is specified
        if not args.keep:
            try:
                os.remove(output_file)
                print(f"Temporary Python file deleted.")
            except Exception as e:
                print(f"Warning: Could not delete output file: {e}")
        else:
            print(f"Output Python file preserved at: {output_file}")
    
    except Exception as e:
        print(f"Compilation error: {e}")
        if args.verbose or args.debug:
            traceback.print_exc()

if __name__ == "__main__":
    main()