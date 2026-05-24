#!/usr/bin/env python3
"""Hawkeyes CLI entry point."""

import argparse
import re
import signal
import sys
import threading
import time
from typing import List, Optional

from hawkeyes import __version__
from hawkeyes.banner import print_banner
from hawkeyes.scanner import TCPPortScanner
from hawkeyes.utils.formatter import ResultFormatter
from hawkeyes.utils.port_parser import PortParsingError, parse_port_specification


class ScanInterruptedException(Exception):
    """Raised when the user interrupts a scan."""


def _is_valid_ipv4(ip: str) -> bool:
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        return False
    return all(int(octet) <= 255 for octet in ip.split('.'))


def _is_valid_hostname(hostname: str) -> bool:
    pattern = (
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )
    return re.match(pattern, hostname) is not None


def validate_target(target: str) -> str:
    if not target or not target.strip():
        raise argparse.ArgumentTypeError("Target cannot be empty")

    target = target.strip()
    if _is_valid_ipv4(target) or _is_valid_hostname(target):
        return target

    raise argparse.ArgumentTypeError(
        f"Invalid target: {target}. Must be valid IP address or domain name."
    )


def validate_ports(ports: str) -> str:
    try:
        parse_port_specification(ports)
        return ports
    except PortParsingError as e:
        raise argparse.ArgumentTypeError(str(e)) from e


def validate_threads(threads: int) -> int:
    if threads < 1:
        raise argparse.ArgumentTypeError("Thread count must be at least 1")
    if threads > 1000:
        raise argparse.ArgumentTypeError("Thread count cannot exceed 1000")
    return threads


def validate_timeout(timeout: float) -> float:
    if timeout <= 0:
        raise argparse.ArgumentTypeError("Timeout must be greater than 0")
    if timeout > 30:
        raise argparse.ArgumentTypeError("Timeout cannot exceed 30 seconds")
    return timeout


def _signal_handler(signum, frame):
    raise ScanInterruptedException("Scan interrupted by user (Ctrl+C)")


def _setup_signal_handlers() -> None:
    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, _signal_handler)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hawk',
        description='Hawkeyes - Multithreaded TCP Port Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: hawk target example.com --ports "80,443,8080"',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'Hawkeyes {__version__}',
    )

    subparsers = parser.add_subparsers(dest='command')

    target_parser = subparsers.add_parser(
        'target',
        help='Scan TCP ports on a target host',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: hawk target example.com --ports "80,443"',
    )
    target_parser.add_argument(
        'host',
        type=validate_target,
        help='Target IP address or domain name',
    )
    target_parser.add_argument(
        '--ports',
        default='1-1000',
        type=validate_ports,
        help='Ports to scan (default: "1-1000")',
    )
    target_parser.add_argument(
        '--threads',
        type=int,
        default=100,
        help='Concurrent threads (default: 100, max: 1000)',
    )
    target_parser.add_argument(
        '--timeout',
        type=float,
        default=1.0,
        help='Connection timeout in seconds (default: 1.0, max: 30)',
    )
    target_parser.add_argument(
        '--output',
        type=str,
        help='Save results to a JSON file',
    )

    return parser


def _print_scan_configuration(args: argparse.Namespace, port_list: List[int]) -> None:
    print("Hawkeyes Scan Configuration:")
    print(f"  Target: {args.host}")
    print(f"  Ports: {len(port_list)} ports ({args.ports})")
    print(f"  Threads: {args.threads}")
    print(f"  Timeout: {args.timeout}s")
    if args.output:
        print(f"  Output: {args.output}")
    print()


def _handle_network_error(error: OSError, target: str) -> None:
    error_code = getattr(error, 'errno', None)
    if error_code == 113:
        print(f"Network error: No route to host '{target}'")
        print("Please check network connectivity and target accessibility.")
    elif error_code == 101:
        print("Network error: Network is unreachable")
        print("Please check your network connection.")
    else:
        print(f"Network error ({error_code}): {error}")


def _execute_scan(
    scanner: TCPPortScanner,
    args: argparse.Namespace,
    port_list: List[int],
) -> dict:
    try:
        summary = scanner.scan_ports(
            target=args.host,
            ports=port_list,
            max_threads=args.threads,
        )
        return summary.to_dict()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except ConnectionRefusedError:
        print("Connection refused: Target is actively refusing connections")
        sys.exit(1)
    except OSError as e:
        _handle_network_error(e, args.host)
        sys.exit(1)
    except ScanInterruptedException:
        print("\nScan interrupted by user. Cleaning up...")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected scan error: {e}")
        print("This may be due to network issues or target configuration.")
        sys.exit(1)


def _format_and_display_results(results: dict, output_file: Optional[str]) -> None:
    try:
        ResultFormatter().print_and_save(results, output_file)
    except Exception as e:
        print(f"Error formatting results: {e}")
        print("Raw results may still be available in memory.")


def _cleanup_resources(scanner: Optional[TCPPortScanner]) -> None:
    if not scanner:
        return
    try:
        if threading.active_count() > 1:
            time.sleep(0.1)
    except Exception:
        pass


def run_target_scan(args: argparse.Namespace) -> Optional[dict]:
    scanner = None
    try:
        _setup_signal_handlers()
        validate_threads(args.threads)
        validate_timeout(args.timeout)

        try:
            port_list = parse_port_specification(args.ports)
        except PortParsingError as e:
            print(f"Port parsing error: {e}")
            sys.exit(1)

        _print_scan_configuration(args, port_list)
        scanner = TCPPortScanner(timeout=args.timeout)
        print("Starting scan...")
        results = _execute_scan(scanner, args, port_list)
        _format_and_display_results(results, args.output)
        return results
    finally:
        _cleanup_resources(scanner)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        print_banner()
        sys.exit(0)

    if args.command == 'target':
        try:
            run_target_scan(args)
        except argparse.ArgumentTypeError as e:
            print(f"Argument error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nScan interrupted by user. Exiting...")
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


if __name__ == '__main__':
    main()
