import os
import re
import sys

def clean_mm2_tokens(code_text):
    """Splits code into parentheses, strings, symbols, and comments."""
    # Remove existing trailing whitespaces per line
    lines = [line.rstrip() for line in code_text.splitlines()]
    
    tokens = []
    for line in lines:
        if not line:
            continue
        # Handle standalone comments
        if line.strip().startswith(';'):
            tokens.append(('COMMENT', line.strip()))
            continue
            
        # Tokenize line using regex (captures parens, symbols, commas)
        line_tokens = re.findall(r'\(|\)|;.*|"[^"]*"|[^\s()]+', line)
        for token in line_tokens:
            if token.startswith(';'):
                tokens.append(('INLINE_COMMENT', token))
            elif token == '(':
                tokens.append(('OPEN', token))
            elif token == ')':
                tokens.append(('CLOSE', token))
            else:
                tokens.append(('SYMBOL', token))
    return tokens

def format_mm2_code(code_text):
    """Formats MM2 tokens matching the 11 style guide rules."""
    tokens = clean_mm2_tokens(code_text)
    if not tokens:
        return code_text

    formatted_lines = []
    indent_level = 0
    current_line = []
    
    for i, (ttype, val) in enumerate(tokens):
        indent = "  " * indent_level
        
        if ttype == 'COMMENT':
            if current_line:
                formatted_lines.append(indent + " ".join(current_line))
                current_line = []
            formatted_lines.append(val)  # Keeps full text comment line
            
        elif ttype == 'OPEN':
            if current_line:
                # Rule 4: Opening parenthesis stays on same line as previous element if applicable
                current_line.append(val)
            else:
                current_line.append(val)
            indent_level += 1
            
        elif ttype == 'CLOSE':
            indent_level = max(0, indent_level - 1)
            if current_line:
                formatted_lines.append("  " * (indent_level + 1) + " ".join(current_line))
                current_line = []
            # Rule 3: Closing parenthesis on its own line aligned with its opening expression
            formatted_lines.append(("  " * indent_level) + ")")
            
        elif ttype == 'SYMBOL':
            # Rule 6: Adjust spacing after commas
            if val == ',':
                current_line.append(val)
            else:
                current_line.append(val)
                
        elif ttype == 'INLINE_COMMENT':
            # Rule 10: Inline comments separated by 2 spaces
            if current_line:
                line_str = " ".join(current_line) + f"  {val}"
                formatted_lines.append("  " * indent_level + line_str)
                current_line = []
            else:
                formatted_lines.append("  " * indent_level + val)

    if current_line:
        formatted_lines.append("  " * indent_level + " ".join(current_line))

    # Clean up empty lines or formatting artifacts
    result = "\n".join(formatted_lines)
    return result + "\n"

def process_markdown_file(file_path):
    """Finds all ```mm2 blocks inside a markdown file and formats them."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex targeting markdown ```mm2 code blocks
    pattern = re.compile(r'(```mm2\s*\n)(.*?)(```)', re.DOTALL)
    
    def replacer(match):
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)
        formatted_body = format_mm2_code(body)
        return f"{prefix}{formatted_body}{suffix}"

    new_content = pattern.sub(replacer, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✓ Formatted MM2 blocks in: {file_path}")

if __name__ == "__main__":
    # If explicit files passed as args, run those. Otherwise run on the default directory.
    if len(sys.argv) > 1:
        files_to_process = sys.argv[1:]
    else:
        target_dir = "structuring_code"
        files_to_process = [
            os.path.join(target_dir, f) 
            for f in os.listdir(target_dir) 
            if f.endswith('.md')
        ] if os.path.exists(target_dir) else []

    for file_path in files_to_process:
        if os.path.exists(file_path):
            process_markdown_file(file_path)