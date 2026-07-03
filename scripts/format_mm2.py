import os
import re
import sys

def format_mm2_code(code_text):
    """
    Formats MM2 code blocks to match the repository style guide rules.
    This includes:
      - Converting non-breaking spaces and tabs to standard spaces.
      - Enforcing strict 2-space indentation.
      - Aligning closing parentheses on their own line for multi-line blocks.
      - Normalizing comments and spacing around commas.
      - Preserving structural empty lines while collapsing consecutive duplicates.
    """
    # Normalize non-breaking spaces and tabs
    code_text = code_text.replace('\xa0', ' ').replace('\t', ' ')
    lines = code_text.splitlines()
    
    formatted_lines = []
    indent_level = 0
    consecutive_empty = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Handle empty lines gracefully to preserve readability
        if not stripped:
            consecutive_empty += 1
            if consecutive_empty <= 1:  # Allow at most one consecutive blank line
                formatted_lines.append("")
            continue
            
        consecutive_empty = 0

        # 1. Rule 10: Handle Standalone Comments
        if stripped.startswith(';'):
            # Standardize comment formatting ('; ' with 1 space)
            comment_content = stripped[1:].strip()
            comment_text = f"; {comment_content}" if comment_content else ";"
            formatted_lines.append(f"{'  ' * indent_level}{comment_text}")
            continue

        # 2. Rule 3 & 7: Dedent before formatting if the line is strictly a closing parenthesis stack
        close_match = re.match(r'^(\)+)$', stripped)
        if close_match:
            close_count = len(close_match.group(1))
            indent_level = max(0, indent_level - close_count)

        # 3. Rule 5 & 6: Clean up internal spacing and commas
        # Collapse multiple spaces down to a single space
        cleaned_line = re.sub(r'\s+', ' ', stripped)
        # Ensure a single space after ',' (Rule 6)
        cleaned_line = re.sub(r',(?!\s)', ', ', cleaned_line)
        
        # 4. Enforce current indentation
        indent_space = '  ' * indent_level
        formatted_lines.append(f"{indent_space}{cleaned_line}")

        # 5. Rule 7: Update indentation level for subsequent lines based on net paren balance
        # If the line wasn't solely dedicated to closing parentheses, we calculate the remaining drift
        if not close_match:
            open_count = stripped.count('(')
            close_count_all = stripped.count(')')
            indent_level += (open_count - close_count_all)
            indent_level = max(0, indent_level)

    # Clean up trailing/leading blank lines
    result_text = '\n'.join(formatted_lines).strip()
    return result_text + '\n' if result_text else ''

def looks_like_mm2_block(text):
    """
    Utility to inspect plain markdown code fence contents and determine 
    if they contain MM2 code blocks based on common syntax markers.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('(') or stripped.startswith(';'):
            return True
        if '$' in stripped or 'exec' in stripped:
            return True
    return False

def process_markdown_file(file_path):
    """
    Finds and updates all ```mm2 or unlabeled MM2 blocks inside a markdown file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We dynamically construct the three backticks sequence to avoid issues
    # with markdown parsers when nesting fences in a code block.
    ticks = '`' * 3
    pattern = re.compile(rf'({ticks}(?:mm2)?\s*\n)(.*?)({ticks})', re.DOTALL)

    def replacer(match):
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)
        if 'mm2' in prefix or looks_like_mm2_block(body):
            formatted_body = format_mm2_code(body)
            return f"{prefix}{formatted_body}{suffix}"
        return match.group(0)

    new_content = pattern.sub(replacer, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Formatted MM2 blocks in markdown: {file_path}")

def process_raw_mm2_file(file_path):
    """
    Formats standalone .mm2 program files directly.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    formatted_content = format_mm2_code(content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_content)

    print(f"✓ Formatted standalone MM2 file : {file_path}")

def main():
    # Check if user passed the --check flag anywhere in arguments
    check_mode = "--check" in sys.argv
    
    # Remove --check from argument processing list if present
    args = [a for a in sys.argv[1:] if a != "--check"]
    
    if len(args) > 0:
        files_to_process = args
    else:
        target_dir = 'structuring_code'
        mm2_programs_dir = os.path.join(target_dir, 'mm2_programs')
        files_to_process = []
        
        if os.path.exists(target_dir):
            for f in os.listdir(target_dir):
                if f.endswith('.md'):
                    files_to_process.append(os.path.join(target_dir, f))
                    
        if os.path.exists(mm2_programs_dir):
            for f in os.listdir(mm2_programs_dir):
                if f.endswith('.mm2'):
                    files_to_process.append(os.path.join(mm2_programs_dir, f))

    if not files_to_process:
        print('No files discovered or provided for processing.')
        sys.exit(0)

    mismatches = 0

    for file_path in files_to_process:
        if os.path.exists(file_path):
            # Read original content to compare later
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Format the body text natively
            formatted_content = format_mm2_code(original_content) if file_path.endswith('.mm2') else None
            
            # If markdown, we'd need to mock the regex replacement comparison
            # For simplicity, we compare if the file changes after processing
            if file_path.endswith('.md'):
                process_markdown_file(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                if original_content != new_content:
                    mismatches += 1
                    if check_mode:
                        # Revert the file change if we are only checking
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(original_content)
            elif file_path.endswith('.mm2'):
                if original_content != formatted_content:
                    mismatches += 1
                    if not check_mode:
                        process_raw_mm2_file(file_path)

            # Print log based on mode
            if original_content != (formatted_content if file_path.endswith('.mm2') else new_content):
                if check_mode:
                    print(f"❌ File requires formatting: {file_path}")
        else:
            print(f'Skipping missing file: {file_path}')

    # Exit strategies based on validation state
    if check_mode and mismatches > 0:
        print(f"\n❌ Error: {mismatches} file(s) failed style verification guidelines.")
        sys.exit(1)
    elif check_mode:
        print("✅ Success: All files are perfectly formatted!")
        sys.exit(0)

if __name__ == '__main__':
    main()