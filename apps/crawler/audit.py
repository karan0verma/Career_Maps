import os
import ast
import json

def analyze_file(filepath):
    results = {
        'bare_excepts': [],
        'missing_type_hints': [],
        'requests_no_timeout': [],
        'print_statements': [],
        'todo_comments': []
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
    for i, line in enumerate(lines):
        if 'TODO' in line or 'todo' in line.lower() and '#' in line:
            results['todo_comments'].append(i+1)
        if 'print(' in line:
            results['print_statements'].append(i+1)
        if 'requests.get(' in line and 'timeout=' not in line:
            results['requests_no_timeout'].append(i+1)
        if 'requests.post(' in line and 'timeout=' not in line:
            results['requests_no_timeout'].append(i+1)

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == 'Exception'):
                    results['bare_excepts'].append(node.lineno)
            if isinstance(node, ast.FunctionDef):
                if node.returns is None and node.name != '__init__':
                    results['missing_type_hints'].append(f"{node.name} (line {node.lineno})")
    except Exception:
        pass
        
    return results

def main():
    root_dir = 'src'
    audit_results = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.py'):
                filepath = os.path.join(dirpath, f)
                res = analyze_file(filepath)
                if any(res.values()):
                    audit_results[filepath] = res
                    
    with open('audit_raw.json', 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2)

if __name__ == '__main__':
    main()
