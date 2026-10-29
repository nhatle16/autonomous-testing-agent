import ast
from pathlib import Path
from langchain.tools import tool


def _describe_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
    parameters = [arg for arg in node.args.args]
    description = ast.get_docstring(node)

    return {
        "name": node.name,
        "docstring": description,
        "arguments": [arg.arg for arg in parameters]
    }

def read_source_code(source: str) -> list[dict] | dict[str, str]:
    """
    Read the source code and extract function definitions along with their docstrings and arguments.

    Args:
        source (str): The source code to parse.

        Returns:
            list[dict] | dict[str, str]: A list of function descriptions, or an
            error dictionary if the source has a syntax error.
            """
    try:
        # Parse the source code into an AST
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Source code:{e.lineno}: {e.msg}"}

    # Keep the top-level function nodes
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    results = [_describe_function(func) for func in functions]
    return results

@tool
def read_input(text: str | None = None,
path: str | None = None) -> list[dict] | dict[str, str]:
    """Read a function definition as a raw text input or from a file path.

    Args:
        text (str | None, optional): The raw text of the function definition. Defaults to None.
        path (str | None, optional): The path to the file containing the function definition. Defaults to None.

        Raises:
            ValueError: If neither text nor path is provided.

            Returns:
                list[dict] | dict[str, str]: A list of function descriptions, or an
                error dictionary if the source has a syntax error.
                """
    if text is not None:
        source = text
    elif path is not None:
        source = Path(path).read_text(encoding="utf-8")
    else:
        raise ValueError("Provide code or a file")

    return read_source_code(source)
