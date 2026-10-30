import ast
from pathlib import Path

from langchain.tools import tool


def _param(arg: ast.arg, kind: str, default: ast.expr | None) -> dict:
    """Describe a function parameter."""
    return {
        "name": arg.arg,
        "kind": kind,
        "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
        "default": ast.unparse(default) if default else None
    }

def _describe_parameters(args: ast.arguments) -> list[dict]:
    """Describe the parameters of a function."""
    # Collect positional-only and regular positional parameters, along with their defaults
    positional = args.posonlyargs + args.args
    # Map positional parameters to their defaults, filling in None for those without defaults
    defaults = [None] * (len(positional) - len(args.defaults)) + args.defaults
    n_posonly = len(args.posonlyargs)

    params = []
    # Adding positional parameters with their kinds and defaults
    for i, (arg, default) in enumerate(zip(positional, defaults)):
        kind = "positional_only" if i < n_posonly else "positional"
        params.append(_param(arg, kind, default))

    # Variable-length positional parameter (*args)
    if args.vararg:
        params.append(_param(args.vararg, "var_positional", None))
    # Keyword-only parameters with their defaults
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        params.append(_param(arg, "keyword_only", default))
    # Variable-length keyword parameter (**kwargs)
    if args.kwarg:
        params.append(_param(args.kwarg, "var_keyword", None))

    return params

def _describe_function(node: ast.FunctionDef | ast.AsyncFunctionDef, source: str) -> dict:
    parameters = _describe_parameters(node.args)
    docstring = ast.get_docstring(node)

    return {
        "name": node.name,
        "docstring": docstring,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "parameters": parameters,
        "returns": ast.unparse(node.returns) if node.returns else None,
        "source": ast.get_source_segment(source, node)
    }

def read_source_code(source: str) -> list[dict] | dict[str, str]:
    """
    Read the source code and extract function definitions along with their docstrings and arguments.

    Args:
        source (str): The source code to parse.

    Returns:
        list[dict] | dict[str, str]: A list of top-level function descriptions, or an
        error dictionary if the source has a syntax error or contains no top-level functions.
    """
    try:
        # Parse the source code into an AST
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Source code:{e.lineno}: {e.msg}"}

    # Keep the top-level function nodes
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    # No function in the source code
    if not functions:
        return {"error": "No top-level function found"}

    results = [_describe_function(func, source) for func in functions]
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
        list[dict] | dict[str, str]: A list of top-level function descriptions, or an
        error dictionary if the source has a syntax error or contains no top-level functions.
    """
    if text is not None:
        source = text
    elif path is not None:
        source = Path(path).read_text(encoding="utf-8")
    else:
        raise ValueError("Provide code or a file")

    return read_source_code(source)
