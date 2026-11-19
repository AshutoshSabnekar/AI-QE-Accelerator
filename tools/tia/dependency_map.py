"""
Manual dependency map for Test Impact Analysis.

DEPENDENCIES:
    Maps a function to the functions that directly depend on it.

FUNCTION_TEST_MARKERS:
    Maps each function to its corresponding pytest marker.
"""

DEPENDENCIES = {
    "validate_number": ["square_root", "factorial"],
}

FUNCTION_TEST_MARKERS = {
    "add": ["addition"],
    "subtract": ["subtraction"],
    "multiply": ["multiplication"],
    "divide": ["division"],
    "modulus": ["modulus"],
    "power": ["power"],
    "square_root": ["square_root"],
    "factorial": ["factorial"],
}