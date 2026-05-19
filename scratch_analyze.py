import os
import sys
import py_compile

def check_syntax(directory):
    errors = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append((path, str(e)))
    return errors

def search_terms(directory, terms):
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            for term in terms:
                                if term in line and not line.strip().startswith('#'):
                                    results.append((path, i + 1, line.strip(), term))
                except Exception as e:
                    pass
    return results

if __name__ == '__main__':
    bot_dir = 'c:\\Users\\SHREE\\OneDrive\\Desktop\\DestinyBot-main\\DestinyBot-main\\DestinyBot'
    print("=== SYNTAX CHECK ===")
    errors = check_syntax(bot_dir)
    if errors:
        for path, err in errors:
            print(f"Syntax error in {path}:\n{err}\n")
    else:
        print("No syntax errors found!")

    print("\n=== SEARCHING FOR REMOVED MODULES ===")
    terms = ['pymongo', 'motor', 'mongo']
    occurrences = search_terms(bot_dir, terms)
    if occurrences:
        for path, line_no, content, term in occurrences:
            print(f"Match for '{term}' in {path}:{line_no} -> {content}")
    else:
        print("No remnants of removed database modules found.")
