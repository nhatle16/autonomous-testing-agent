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

def read_input(text: str | None = None,
               path: str | None = None):
    """Read a function definition as a raw text input or from a file path.

    Args:
        text (str | None, optional): The raw text of the function definition. Defaults to None.
        path (str | None, optional): The path to the file containing the function definition. Defaults to None.

    Raises:
        ValueError: If neither text nor path is provided.

    Returns:
        _type_: _description_
    """
    if text is not None:
        source = text
    elif path is not None:
        source = Path(path).read_text(encoding="utf-8")
    else:
        raise ValueError("Provide code or a file")
    
    return read_source_code(source)

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
