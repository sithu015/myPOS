# -*- coding: utf-8 -*-
import argparse
import sys
import os

def validate_corpus(input_stream, output_stream, verbose):
    """
    Validates a POS-tagged corpus file for common errors.
    
    Args:
        input_stream: A file-like object to read the corpus from.
        output_stream: A file-like object to write the validation report to.
        verbose (bool): If True, prints a detailed report with statistics.
    """
    # Counters to track different types of errors
    total_lines = 0
    blank_lines = 0
    lines_with_windows_endings = 0
    lines_with_invalid_tokens = 0
    
    # List to store the details of each problematic line
    error_log = []

    for line_number, original_line in enumerate(input_stream, 1):
        total_lines += 1
        line = original_line.strip()
        
        # Keep track of errors on the current line
        current_line_errors = []

        # Check for Windows line endings (\r\n)
        if original_line.endswith('\r\n'):
            lines_with_windows_endings += 1
            current_line_errors.append("Windows line ending detected.")
        
        # Check for blank lines or lines with only whitespace
        if not line:
            blank_lines += 1
            current_line_errors.append("Blank line or line with only whitespace.")
        else:
            # If the line is not blank, check the token format
            tokens = line.split()
            has_invalid_token = False
            for token in tokens:
                # A valid token should have at least one character, a '/', and then a tag.
                # This check catches untagged words, malformed tags like 'word/', or 'word//tag'.
                if '/' not in token or token.startswith('/') or token.endswith('/') or token.count('/') > 1:
                    lines_with_invalid_tokens += 1
                    current_line_errors.append(f"Invalid token format: '{token}'. Expected 'word/tag'.")
                    has_invalid_token = True
                    break # Stop checking this line as an error is already found
        
        # If any errors were found on this line, add it to the error log
        if current_line_errors:
            error_log.append({
                'line_number': line_number,
                'original_line': original_line.strip(),
                'errors': current_line_errors
            })

    # --- Print the final report based on the verbose flag ---
    if verbose:
        output_stream.write("--- Corpus Validation Report (Verbose) ---\n")
        output_stream.write(f"Total lines processed: {total_lines}\n\n")
        output_stream.write("### Error Summary ###\n")
        output_stream.write(f"1. Lines with Windows line endings: {lines_with_windows_endings}\n")
        output_stream.write(f"2. Blank lines: {blank_lines}\n")
        output_stream.write(f"3. Lines with invalid token format (e.g., untagged words): {lines_with_invalid_tokens}\n\n")
        
        if error_log:
            output_stream.write("### Detailed Errors ###\n")
            for entry in error_log:
                output_stream.write(f"Line {entry['line_number']}: {entry['original_line']}\n")
                for error in entry['errors']:
                    output_stream.write(f"  - {error}\n")
                output_stream.write("\n")
        else:
            output_stream.write("No errors found in the corpus.\n")

    else: # Default output (non-verbose)
        if error_log:
            output_stream.write("--- Corpus Validation Report ---\n")
            output_stream.write("The following lines contain errors:\n\n")
            for entry in error_log:
                output_stream.write(f"Line {entry['line_number']}: {entry['original_line']}\n")
        else:
            output_stream.write("No errors found in the corpus.\n")

def main():
    """
    Main function to parse arguments and run the validator.
    """
    parser = argparse.ArgumentParser(
        description="Validate a POS-tagged Myanmar corpus file.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Usage Examples:
    # Validate a file and print errors to the console (default behavior)
    python validate_corpus.py --input train.txt
    
    # Validate a file and save a detailed report to an output file
    python validate_corpus.py --input train.txt --output validation_report.log --verbose

    # Validate corpus from stdin (default behavior)
    cat train.txt | python validate_corpus.py
"""
    )
    
    parser.add_argument(
        '--input', 
        metavar='FILE', 
        type=str, 
        help="Path to the input corpus file (reads from stdin if not specified)."
    )

    parser.add_argument(
        '--output', 
        metavar='FILE', 
        type=str, 
        help="Path to the output file for the report (writes to stdout if not specified)."
    )

    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help="Enable verbose output with statistics for each error category."
    )

    args = parser.parse_args()

    # Determine input and output streams based on arguments
    input_stream = sys.stdin
    output_stream = sys.stdout

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
            sys.exit(1)
        input_stream = open(args.input, 'r', encoding='utf-8')

    if args.output:
        try:
            output_stream = open(args.output, 'w', encoding='utf-8')
        except IOError as e:
            print(f"Error: Could not open output file '{args.output}'. {e}", file=sys.stderr)
            sys.exit(1)
    
    # Run the validation
    try:
        validate_corpus(input_stream, output_stream, args.verbose)
    finally:
        # Ensure streams are closed correctly
        if args.input:
            input_stream.close()
        if args.output:
            output_stream.close()

if __name__ == "__main__":
    main()
