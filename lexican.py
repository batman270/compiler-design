import re

# Token patterns (order matters: specific before generic)
TOKEN_SPECIFICATION = [
    ('NUMBER',     r'\d+(\.\d*)?'),       # Integer or decimal number
    ('IDENTIFIER', r'[A-Za-z_]\w*'),      # Identifiers
    ('ASSIGN',     r'='),                 # Assignment operator
    ('OPERATOR',   r'[+\-*/]'),           # Arithmetic operators
    ('LPAREN',     r'\('),                # Left parenthesis
    ('RPAREN',     r'\)'),                # Right parenthesis
    ('SKIP',       r'[ \t]+'),            # Skip spaces and tabs
    ('NEWLINE',    r'\n'),                # Newlines (optional)
    ('MISMATCH',   r'.'),                 # Any other character (error)
]

def lex(source_code):
    token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
    for match in re.finditer(token_regex, source_code):
        kind = match.lastgroup
        value = match.group(kind)
        if kind in ('SKIP', 'NEWLINE'):
            continue
        if kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character: {value!r}")
        yield (kind, value)

# Test the lexical analyzer
if __name__ == '__main__':
    source_code = "x = 3.14 + 42"
    for token in lex(source_code):
        print(token)