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
    """
    # Normalize non-breaking spaces and tabs
    code_text = code_text.replace('\xa0', ' ').replace('\t', ' ')
    lines = code_text.splitlines()
    
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
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

    return '\n'.join(formatted_lines) + '\n'

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

    # Match code blocks: ```mm2 or plain ``` fences
    pattern = re.compile(r'(```(?:mm2)?\s*\n)(.*?)(```)', re.DOTALL)

    def replacer(match):
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)
        if prefix.startswith('```mm2') or looks_like_mm2_block(body):
            formatted_body = format_mm2_code(body)
            return f"{prefix}{formatted_body}{suffix}"
        return match.group(0)

    new_content = pattern.sub(replacer, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Formatted MM2 blocks in: {file_path}")


def main():
    if len(sys.argv) > 1:
        files_to_process = sys.argv[1:]
    else:
        target_dir = 'structuring_code'
        files_to_process = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if f.endswith('.md')
        ] if os.path.exists(target_dir) else []

    if not files_to_process:
        print('No files to process.')
        return

    for file_path in files_to_process:
        if os.path.exists(file_path):
            process_markdown_file(file_path)
        else:
            print(f'Skipping missing file: {file_path}')


if __name__ == '__main__':
    main()
