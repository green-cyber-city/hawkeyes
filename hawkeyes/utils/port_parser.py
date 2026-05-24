#!/usr/bin/env python3
"""
Port parsing utility for the TCP Port Scanner.

This module provides functions to parse and validate port specifications
in various formats like ranges (1-1000) and comma-separated lists (22,80,443).

Author: TCP Port Scanner Team
Version: 1.0.0
"""

import re
from typing import List, Union


class PortParsingError(Exception):
    """
    Custom exception for port parsing errors.
    
    Raised when the port specification format is invalid or contains
    out-of-bounds port numbers.
    """
    pass


def parse_port_specification(port_spec: str) -> List[int]:
    """
    Parse a port specification string into a list of port numbers.
    
    This function accepts various port specification formats:
    - Single ports: "80"
    - Port ranges: "1-1000"
    - Comma-separated lists: "22,80,443"
    - Mixed formats: "22,80,443,8000-9000"
    
    Args:
        port_spec (str): Port specification string to parse
        
    Returns:
        List[int]: Sorted list of unique port numbers
        
    Raises:
        PortParsingError: If port specification is invalid, contains
                         out-of-bounds ports, or is malformed
        
    Example:
        >>> parse_port_specification("22,80,443")
        [22, 80, 443]
        >>> parse_port_specification("1-1000")
        list(range(1, 1001))
    """
    # Validate input type
    if not port_spec or not isinstance(port_spec, str):
        raise PortParsingError("Port specification must be a non-empty string")
    
    # Clean and validate the input
    port_spec = port_spec.strip()
    if not port_spec:
        raise PortParsingError("Port specification cannot be empty")
    
    # Check for valid characters only
    if not re.match(r'^[\d,\-\s]+$', port_spec):
        raise PortParsingError("Port specification can only contain numbers, commas, hyphens, and spaces")
    
    ports = []
    port_parts = port_spec.split(',')
    
    # Process each port or port range
    for i, part in enumerate(port_parts):
        part = part.strip()
        if not part:
            raise PortParsingError(f"Empty port specification at position {i + 1}")
        
        try:
            if '-' in part:
                # Handle port range like "1-1000"
                _validate_and_parse_range(part, ports)
            else:
                # Handle single port like "80"
                _validate_and_parse_single_port(part, ports)
                
        except ValueError as e:
            if "invalid literal" in str(e):
                raise PortParsingError(f"Invalid port number in: '{part}'")
            raise PortParsingError(f"Error parsing port specification: {e}")
    
    # Remove duplicates and sort
    unique_ports = sorted(list(set(ports)))
    
    if not unique_ports:
        raise PortParsingError("No valid ports found in specification")
    
    return unique_ports


def _validate_and_parse_range(range_str: str, ports: List[int]) -> None:
    """
    Validate and parse a port range specification.
    
    Args:
        range_str (str): Port range string like "1-1000"
        ports (List[int]): List to append parsed ports to
        
    Raises:
        PortParsingError: If range format is invalid or out of bounds
    """
    if range_str.count('-') > 1:
        raise PortParsingError(f"Invalid port range format: '{range_str}'")
    
    start_str, end_str = range_str.split('-')
    if not start_str or not end_str:
        raise PortParsingError(f"Invalid port range: '{range_str}'")
    
    start = int(start_str)
    end = int(end_str)
    
    # Validate port bounds
    if start < 1 or start > 65535:
        raise PortParsingError(f"Start port out of bounds (1-65535): {start}")
    if end < 1 or end > 65535:
        raise PortParsingError(f"End port out of bounds (1-65535): {end}")
    if start > end:
        raise PortParsingError(f"Start port cannot be greater than end port: {start}-{end}")
    
    # Prevent creating huge port lists
    if (end - start + 1) > 10000:
        raise PortParsingError(f"Port range too large (max 10000 ports): {start}-{end}")
    
    # Add all ports in the range
    ports.extend(range(start, end + 1))


def _validate_and_parse_single_port(port_str: str, ports: List[int]) -> None:
    """
    Validate and parse a single port specification.
    
    Args:
        port_str (str): Single port string like "80"
        ports (List[int]): List to append parsed port to
        
    Raises:
        PortParsingError: If port number is invalid or out of bounds
    """
    port_num = int(port_str)
    if port_num < 1 or port_num > 65535:
        raise PortParsingError(f"Port out of bounds (1-65535): {port_num}")
    ports.append(port_num)


def validate_port_list(ports: List[int]) -> List[int]:
    """
    Validate a list of port numbers.
    
    This function ensures all elements in the list are valid port numbers
    within the TCP port range (1-65535).
    
    Args:
        ports (List[int]): List of port numbers to validate
        
    Returns:
        List[int]: The same list if all ports are valid
        
    Raises:
        PortParsingError: If the list is empty, not a list, or contains
                         invalid port numbers
        
    Example:
        >>> validate_port_list([80, 443])
        [80, 443]
        >>> validate_port_list([0])
        PortParsingError: Port out of bounds (1-65535): 0
    """
    # Validate input list
    if not ports:
        raise PortParsingError("Port list cannot be empty")
    
    if not isinstance(ports, list):
        raise PortParsingError("Ports must be provided as a list")
    
    # Validate each port in the list
    valid_ports = []
    for port in ports:
        if not isinstance(port, int):
            raise PortParsingError(f"Port must be an integer: {port}")
        if port < 1 or port > 65535:
            raise PortParsingError(f"Port out of bounds (1-65535): {port}")
        valid_ports.append(port)
    
    return valid_ports


# Example usage and test cases
def run_tests() -> None:
    """
    Run comprehensive tests for the port parsing functionality.
    
    This function tests both valid and invalid port specifications
    to ensure the parser works correctly and handles edge cases.
    """
    # Valid test cases
    valid_test_cases = [
        ("80", [80]),
        ("22,80,443", [22, 80, 443]),
        ("1-1000", list(range(1, 1001))),
        ("22,80,443,8000-9000", [22, 80, 443] + list(range(8000, 9001))),
        ("  22 , 80 , 443  ", [22, 80, 443]),  # with spaces
        ("80-80", [80]),  # single port as range
    ]
    
    # Error test cases
    error_test_cases = [
        "",  # empty string
        "  ",  # whitespace only
        "invalid",  # non-numeric
        "0",  # port too low
        "65536",  # port too high
        "22,80,invalid",  # mixed valid/invalid
        "1000-1",  # invalid range (start > end)
        "1-65536",  # end out of bounds
        "0-1000",  # start out of bounds
        "1-100000",  # too large range
        "22,,80",  # empty port in list
        "22-80-443",  # too many hyphens
    ]
    
    print("=== Port Parser Test Suite ===\n")
    
    print("✅ Valid Test Cases:")
    for test_input, expected in valid_test_cases:
        try:
            result = parse_port_specification(test_input)
            success = len(result) == len(expected) and set(result) == set(expected)
            status = "PASS" if success else "FAIL"
            print(f"  {status}: '{test_input}' -> {len(result)} ports")
        except PortParsingError as e:
            print(f"  FAIL: '{test_input}' -> UNEXPECTED ERROR: {e}")
    
    print("\n❌ Error Test Cases:")
    for test_input in error_test_cases:
        try:
            result = parse_port_specification(test_input)
            print(f"  FAIL: '{test_input}' -> UNEXPECTED SUCCESS: {result}")
        except PortParsingError as e:
            print(f"  PASS: '{test_input}' -> EXPECTED ERROR: {e}")


if __name__ == "__main__":
    run_tests()