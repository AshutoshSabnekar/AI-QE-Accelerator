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

def square_root(a):
    if isinstance(a, bool) or not isinstance(a, (int, float)):
        raise TypeError("Square root input must be an integer or float")
    if a < 0:
        raise ValueError("Cannot take the square root of a negative number")
    return a ** 0.5

def factorial(n):
    """Return n! for a non-negative integer."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("Factorial input must be a non-negative integer")
    if n < 0:
        raise ValueError("Cannot take the factorial of a negative number")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result   
