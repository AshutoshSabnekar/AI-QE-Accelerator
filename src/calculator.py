def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b 

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def modulus(a, b):
    if b == 0:
        raise ValueError("Cannot take modulus by zero")
    return a % b    

def power(a, b):
    return a ** b

def validate_number(value, function_name, allowed_types=(int, float)):
    if isinstance(value, bool) or not isinstance(value, allowed_types):
        expected_type = (
            "a non-negative integer"
            if allowed_types == (int,)
            else "an integer or float"
        )
        raise TypeError(f"{function_name} input must be {expected_type}")

def square_root(a):
    validate_number(a, "Square root")
    if a < 0:
        raise ValueError("Cannot take the square root of a negative number")
    return a ** 0.5

def factorial(n):
    """Return n! for a non-negative integer."""
    validate_number(n, "Factorial", allowed_types=(int,))
    if n < 0:
        raise ValueError("Cannot take the factorial of a negative number")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
