#!/usr/bin/env python3
"""
TCP Port Scanner - Main Entry Point

A multithreaded TCP port scanner for educational cybersecurity purposes.
This tool scans specified ports on a target and identifies open services
with banner grabbing capabilities.

Author: TCP Port Scanner Team
Version: 1.0.0
"""

import argparse
import sys
import re
import signal
from typing import List, Optional

# Import utility modules
from utils.port_parser import parse_port_specification, PortParsingError
from utils.services import get_service_name
from utils.banner_grabber import BannerGrabber
from utils.formatter import ResultFormatter

# Import scanner module
from scanner import TCPPortScanner


def validate_target(target: str) -> str:
    """
    Validate and clean the target IP address or domain name.
    
    This function validates IPv4 addresses and domain names to ensure
    they are properly formatted and within valid ranges.
    
    Args:
        target (str): Target IP address or domain name to validate
        
    Returns:
        str: Cleaned target string if valid
        
    Raises:
        argparse.ArgumentTypeError: If target format is invalid
        
    Examples:
        >>> validate_target("192.168.1.1")
        '192.168.1.1'
        >>> validate_target("example.com")
        'example.com'
        >>> validate_target("invalid@host")
        argparse.ArgumentTypeError
    """
    if not target or len(target.strip()) == 0:
        raise argparse.ArgumentTypeError("Target cannot be empty")
    
    target = target.strip()
    
    # IPv4 address validation
    if _is_valid_ipv4(target):
        return target
    
    # Domain name validation
    if _is_valid_hostname(target):
        return target
    
    raise argparse.ArgumentTypeError(
        f"Invalid target: {target}. Must be valid IP address or domain name."
    )


def _is_valid_ipv4(ip: str) -> bool:
    """
    Check if a string is a valid IPv4 address.
    
    Args:
        ip (str): IP address string to validate
        
    Returns:
        bool: True if valid IPv4 address, False otherwise
    """
    import re
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ipv4_pattern, ip):
        return False
    
    # Check each octet is within valid range (0-255)
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    
    return True


def _is_valid_hostname(hostname: str) -> bool:
    """
    Check if a string is a valid hostname/domain name.
    
    Args:
        hostname (str): Hostname string to validate
        
    Returns:
        bool: True if valid hostname, False otherwise
    """
    import re
    # RFC compliant hostname validation
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(hostname_pattern, hostname) is not None


def validate_ports(ports: str) -> str:
    """
    Validate port specification format for argument parsing.
    
    Args:
        ports (str): Port specification string from command line
        
    Returns:
        str: Original port string if valid
        
    Raises:
        argparse.ArgumentTypeError: If port specification is invalid
    """
    try:
        parsed_ports = parse_port_specification(ports)
        return ports
    except PortParsingError as e:
        raise argparse.ArgumentTypeError(str(e))


def validate_threads(threads: int) -> int:
    """
    Validate thread count for argument parsing.
    
    Args:
        threads (int): Thread count from command line
        
    Returns:
        int: Validated thread count
        
    Raises:
        argparse.ArgumentTypeError: If thread count is invalid
    """
    if threads < 1:
        raise argparse.ArgumentTypeError("Thread count must be at least 1")
    if threads > 1000:
        raise argparse.ArgumentTypeError("Thread count cannot exceed 1000")
    return threads


def validate_timeout(timeout: float) -> float:
    """
    Validate connection timeout for argument parsing.
    
    Args:
        timeout (float): Timeout value from command line
        
    Returns:
        float: Validated timeout value
        
    Raises:
        argparse.ArgumentTypeError: If timeout is invalid
    """
    if timeout <= 0:
        raise argparse.ArgumentTypeError("Timeout must be greater than 0")
    if timeout > 30:
        raise argparse.ArgumentTypeError("Timeout cannot exceed 30 seconds")
    return timeout


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog='tcp-port-scanner',
        description='Multithreaded TCP Port Scanner for Educational Cybersecurity',
        epilog='Example: python main.py --target example.com --ports 80,443,8080 --threads 200',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--target',
        required=True,
        type=validate_target,
        help='Target IP address or domain name to scan'
    )
    
    parser.add_argument(
        '--ports',
        default='1-1000',
        type=validate_ports,
        help='Ports to scan (e.g., "80,443" or "1-1000" or "22,80,443,8000-9000")'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=100,
        help='Number of concurrent threads (default: 100, max: 1000)'
    )
    
    parser.add_argument(
        '--timeout',
        type=float,
        default=1.0,
        help='Connection timeout in seconds (default: 1.0, max: 30)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Optional JSON file to save scan results'
    )
    
    return parser


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command line arguments.
    
    Returns:
        argparse.Namespace: Parsed and validated arguments
        
    Raises:
        argparse.ArgumentTypeError: If any argument is invalid
    """
    parser = create_argument_parser()
    return parser.parse_args()


class ScanInterruptedException(Exception):
    """
    Custom exception for graceful scan interruption.
    
    Raised when the user interrupts the scan with Ctrl+C or other signals.
    """
    pass


def signal_handler(signum, frame):
    """
    Handle interruption signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    raise ScanInterruptedException("Scan interrupted by user (Ctrl+C)")


def setup_signal_handlers():
    """
    Setup signal handlers for graceful shutdown.
    
    This function configures signal handlers for SIGINT (Ctrl+C) and
    SIGTERM to allow clean shutdown of the scanner.
    """
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


def main() -> Optional[dict]:
    """
    Main entry point with comprehensive error handling.
    
    This function orchestrates the entire scanning process:
    1. Parse and validate command line arguments
    2. Setup signal handlers for graceful shutdown
    3. Parse port specifications
    4. Initialize and run the scanner
    5. Format and display results
    6. Handle cleanup on exit
    
    Returns:
        Optional[dict]: Scan results dictionary if successful, None otherwise
        
    Raises:
        SystemExit: On any error condition or user interruption
    """
    scan_summary = None
    scanner = None
    
    try:
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()
        
        # Parse and validate arguments
        args = parse_arguments()
        
        # Validate parsed arguments
        validate_threads(args.threads)
        validate_timeout(args.timeout)
        
        # Parse ports into list with error handling
        try:
            port_list = parse_port_specification(args.ports)
        except PortParsingError as e:
            print(f"Port parsing error: {e}")
            sys.exit(1)
        
        # Display scan configuration
        _print_scan_configuration(args, port_list)
        
        # Initialize scanner
        scanner = TCPPortScanner(timeout=args.timeout)
        
        # Run scan with comprehensive error handling
        print(f"Starting scan...")
        results = _execute_scan(scanner, args, port_list)
        
        # Format and display results
        _format_and_display_results(results, args)
        
        return results
        
    except PortParsingError as e:
        print(f"Port specification error: {e}")
        sys.exit(1)
    except argparse.ArgumentTypeError as e:
        print(f"Argument error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠ Scan interrupted by user. Exiting...")
        sys.exit(130)
    except ScanInterruptedException as e:
        print(f"\n{e}")
        sys.exit(130)
    except MemoryError:
        print("Memory error: Too many ports specified")
        print("Try scanning a smaller port range or reducing thread count.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check your inputs and try again.")
        sys.exit(1)
    finally:
        # Cleanup resources
        _cleanup_resources(scanner)


def _print_scan_configuration(args: argparse.Namespace, port_list: List[int]) -> None:
    """
    Print the scan configuration summary.
    
    Args:
        args: Parsed command line arguments
        port_list: List of ports to be scanned
    """
    print(f"TCP Port Scanner Configuration:")
    print(f"  Target: {args.target}")
    print(f"  Ports: {len(port_list)} ports ({args.ports})")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    if args.output:
        print(f"  Output: {args.output}")
    print()


def _execute_scan(scanner: TCPPortScanner, args: argparse.Namespace, 
                 port_list: List[int]) -> dict:
    """
    Execute the port scan with comprehensive error handling.
    
    Args:
        scanner: Initialized TCPPortScanner instance
        args: Parsed command line arguments
        port_list: List of ports to scan
        
    Returns:
        dict: Scan results dictionary
        
    Raises:
        SystemExit: On any scan error
    """
    try:
        scan_summary = scanner.scan_ports(
            target=args.target,
            ports=port_list,
            max_threads=args.threads
        )
        return scan_summary.to_dict()
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except ConnectionRefusedError:
        print(f"Connection refused: Target is actively refusing connections")
        sys.exit(1)
    except OSError as e:
        _handle_network_error(e, args.target)
        sys.exit(1)
    except ScanInterruptedException:
        print("\n⚠ Scan interrupted by user. Cleaning up...")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected scan error: {e}")
        print("This may be due to network issues or target configuration.")
        sys.exit(1)


def _handle_network_error(error: OSError, target: str) -> None:
    """
    Handle network-related errors with helpful messages.
    
    Args:
        error: The OSError that occurred
        target: Target being scanned
    """
    error_code = getattr(error, 'errno', None)
    
    if error_code == 113:  # No route to host
        print(f"Network error: No route to host '{target}'")
        print("Please check network connectivity and target accessibility.")
    elif error_code == 101:  # Network unreachable
        print(f"Network error: Network is unreachable")
        print("Please check your network connection.")
    else:
        print(f"Network error ({error_code}): {error}")


def _format_and_display_results(results: dict, args: argparse.Namespace) -> None:
    """
    Format and display scan results.
    
    Args:
        results: Scan results dictionary
        args: Parsed command line arguments
    """
    try:
        formatter = ResultFormatter()
        formatter.print_and_save(results, args.output)
    except Exception as e:
        print(f"Error formatting results: {e}")
        print("Raw results may still be available in memory.")
        # Don't exit here as the scan was successful


def _cleanup_resources(scanner: Optional[TCPPortScanner]) -> None:
    """
    Clean up resources on shutdown.
    
    Args:
        scanner: Scanner instance to clean up
    """
    # Cleanup scanner resources
    if scanner:
        try:
            # ThreadPoolExecutor should handle cleanup automatically
            pass
        except:
            pass  # Ignore cleanup errors
    
    # Additional thread cleanup if needed
    try:
        import threading
        if threading.active_count() > 1:
            import time
            time.sleep(0.1)  # Small delay for thread cleanup
    except:
        pass


if __name__ == '__main__':
    main()