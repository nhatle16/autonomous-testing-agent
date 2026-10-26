def add(a, b):
    """Calculates the sum of 2 numbers

    Args:
        a (number): the first number
        b (number): the second number

    Returns:
        number: the sum of the two numbers
    """
    return a + b

def substract(a, b):
    """Calculates the difference of 2 numbers

    Args:
        a (number): the first number
        b (number): the second number

    Returns:
        number: the difference of the two numbers
    """
    return a - b

def multiply(a, b):
    """Calculates the product of 2 numbers

    Args:
        a (number): the first number
        b (number): the second number

    Returns:
        number: the product of the two numbers
    """
    return a * b

def divide(a, b):
    """Calculates the quotient of 2 numbers

    Args:
        a (number): the first number
        b (number): the second number

    Returns:
        number: the quotient of the two numbers
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b