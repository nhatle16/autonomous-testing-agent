import ast
from pathlib import Path

def read_source_code(path: str):
    """Read a file from the provided path and parse its AST.

    Args:
        path (str): path to the file 

    Returns:
        dict: _description_
    """
    source_code = Path(path).read_text()
    
    # Parse the source code into an AST
    tree = ast.parse(source_code)
    print(ast.dump(tree, indent=4))
    
read_source_code("src/samples/sample1.py")