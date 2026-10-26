import ast
from pathlib import Path


def _describe_function(node: ast.FunctionDef) -> dict:
    parameters = [arg for arg in node.args.args]
    description = ast.get_docstring(node)

    return {
        "name": node.name,
        "docstring": description,
        "arguments": [arg.arg for arg in parameters]
    }

def read_source_code(path: str):
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

    # Keep the function nodes
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    results = [_describe_function(func) for func in functions]
    return results


source_parsed = read_source_code("src/samples/sample2.py")

i = 1
for func in source_parsed:
    print(f"----- FUNCTION {i} -----")
    print(f"Function name: {func['name']}")
    print(f"Docstring: {func['docstring']}")
    print(f"Arguments: {func['arguments']}")
    print()
    i += 1