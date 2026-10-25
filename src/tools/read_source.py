import ast
from pathlib import Path

def read_source_code(path: str) -> dict:
    """Read a file from the provided path and parse its AST.

    Args:
        path (str): path to the file

    Returns:
        dict: _description_
    """
    source_code = Path(path).read_text()
    try:
        # Parse the source code into an AST
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"error": f"{path}:{e.lineno}: {e.msg}"}

    # Create a list to hold the functions and classes found in the AST
    functions, classes, imports, others = [], [], [], []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
        else:
            others.append(node)

    return {"path": path, "ast": tree, "functions": functions, "classes": classes, "imports": imports, "others": others}


source_ast = read_source_code("src/samples/sample1.py")
for key in {"functions", "classes", "imports", "others"}:
    print(f"\n{key.upper()}:")
    value = source_ast.get(key)
    if isinstance(value, list) and len(value) > 0:
        print(ast.dump(value[0], indent=4))
    else:
        print(value)