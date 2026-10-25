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
    functions, classes, others = [], [], []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        else:
            others.append(ast.dump(node))
        
    return {"path": path, "ast": tree, "functions": functions, "classes": classes, "others": others}
    
source_ast = read_source_code("src/samples/sample1.py")
for key in source_ast:
    print(f"{key}: {source_ast[key]}")