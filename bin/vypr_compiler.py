#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import traceback
# Update import path to use the module from the src directory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from vypr.compiler import Compiler

def print_header(text, width=60):
    """Print a formatted header with the given text centered."""
    print("\n" + "="*width)
    print(" " * ((width - len(text)) // 2) + text)
    print("="*width + "\n")

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Vypr programming language compiler')
    parser.add_argument('input_file', help='The Vypr source file to compile')
    parser.add_argument('-o', '--output', help='The output Python file name (defaults to input file with .py extension)')
    parser.add_argument('-keep', action='store_true', help='Keep the generated Python file instead of deleting it after execution')
    parser.add_argument('-verbose', action='store_true', help='Show more detailed information during compilation')
    parser.add_argument('-debug', action='store_true', help='Show debug information for development purposes')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Determine output file name if not specified
    output_file = args.output
    if not output_file:
        if args.input_file.endswith('.vy'):
            basename = os.path.basename(args.input_file)[:-3]  # Remove .vy extension
        else:
            basename = os.path.basename(args.input_file)
        
        # Create temporary file in a temporary directory
        if not os.path.exists("temp_py"):
            os.makedirs("temp_py")
        output_file = os.path.join("temp_py", f"{basename}.py")
    
    # Get absolute path for the output file
    output_file = os.path.abspath(output_file)
    
    if args.verbose:
        print(f"Input file: {args.input_file}")
        print(f"Output file: {output_file}")
        with open(args.input_file, 'r') as f:
            source_code = f.read()
            print(f"Source code size: {len(source_code)} bytes, {len(source_code.splitlines())} lines")
            print("\n")
    
    # Compile the Vypr code to Python
    compiler = Compiler()
    with open(args.input_file, 'r') as f:
        source_code = f.read()
    
    success = compiler.compile(source_code, output_file, args.verbose, args.debug)
    
    if not success:
        print(f"Compilation failed: {compiler.get_last_error()}")
        sys.exit(1)
    
    # Run the compiled Python file
    try:
        if args.verbose:
            print_header("EXECUTION")
            print(f"Running compiled code from {output_file}...")
        
        print("\n" + "="*60 + "\n" + " "*20 + "PROGRAM OUTPUT" + " "*20 + "\n" + "="*60 + "\n")
        
        subprocess.run([sys.executable, output_file], check=True)
        
        print("\n" + "="*60 + "\n" + " "*20 + "END OUTPUT" + " "*22 + "\n" + "="*60)
        
        if args.verbose:
            print("\nExecution completed successfully.")
        else:
            print("\nExecution completed.")
    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print(f"Error executing compiled code: {e}")
        print("="*60)
    
    # Delete the output file unless -keep is specified
    if not args.keep:
        try:
            os.remove(output_file)
            if args.verbose:
                print("\nTemporary Python file deleted.")
        except Exception as e:
            print(f"Warning: Could not delete output file: {e}")
    else:
        if args.verbose:
            print("\nOutput Python file preserved at: " + output_file)
        else:
            print(f"Output Python file preserved at: {output_file}")
    
    if args.verbose:
        print_header("COMPILATION COMPLETE")

if __name__ == "__main__":
    main()