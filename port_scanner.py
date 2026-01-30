import socket
import threading
import json
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional


class PortScanner:
    COMMON_SERVICES = {
        20: 'FTP Data',
        21: 'FTP Control',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        993: 'IMAPS',
        995: 'POP3S',
        3389: 'RDP',
        5432: 'PostgreSQL',
        3306: 'MySQL',
        1433: 'MSSQL',
        27017: 'MongoDB',
        6379: 'Redis',
        5984: 'CouchDB'
    }

    def __init__(self, target: str, timeout: float = 1.0, max_threads: int = 100):
        self.target = target
        self.timeout = timeout
        self.max_threads = max_threads
        self.results = {}
        self.lock = threading.Lock()

    def _resolve_target(self) -> str:
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror:
            raise ValueError(f"Cannot resolve hostname: {self.target}")

    def _grab_banner(self, host: str, port: int) -> Optional[str]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3.0)
                sock.connect((host, port))
                
                if port in [80, 8080, 8000]:
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                elif port == 443 or port in [8443, 9443]:
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                elif port == 21:
                    pass
                elif port == 22:
                    pass
                elif port == 25:
                    pass
                else:
                    sock.send(b"HELLO\r\n")
                
                try:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    return banner[:100] if banner else None
                except:
                    return None
                    
        except:
            return None

    def _scan_port(self, host: str, port: int) -> Tuple[int, str, Optional[str]]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                
                if result == 0:
                    status = 'open'
                    banner = self._grab_banner(host, port)
                    return (port, status, banner)
                else:
                    return (port, 'closed', None)
                    
        except socket.timeout:
            return (port, 'filtered', None)
        except Exception:
            return (port, 'filtered', None)

    def scan_ports(self, ports: List[int]) -> Dict:
        host = self._resolve_target()
        print(f"Scanning {host} ({self.target})...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_port = {
                executor.submit(self._scan_port, host, port): port 
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                port, status, banner = future.result()
                
                if status == 'open':
                    service = self.COMMON_SERVICES.get(port, 'Unknown')
                    
                    with self.lock:
                        self.results[port] = {
                            'status': status,
                            'service': service,
                            'banner': banner
                        }
                    
                    print(f"Port {port}/tcp {'open':<8} {service:<15} {banner[:50] if banner else ''}")

        end_time = time.time()
        scan_time = end_time - start_time
        
        summary = {
            'target': self.target,
            'resolved_ip': host,
            'scan_time': round(scan_time, 2),
            'total_ports_scanned': len(ports),
            'open_ports': len(self.results),
            'results': self.results
        }
        
        print(f"\nScan completed in {scan_time:.2f} seconds")
        print(f"Found {len(self.results)} open ports")
        
        return summary

    def parse_ports(self, port_input: str) -> List[int]:
        ports = []
        
        if ',' in port_input:
            port_parts = port_input.split(',')
            for part in port_parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    ports.extend(range(start, end + 1))
                else:
                    ports.append(int(part))
        elif '-' in port_input:
            start, end = map(int, port_input.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(port_input))
        
        return sorted(set(ports))

    def save_results(self, results: Dict, filename: str):
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")


def display_results(results: Dict):
    print(f"\n{'='*60}")
    print(f"SCAN RESULTS FOR {results['target']} ({results['resolved_ip']})")
    print(f"{'='*60}")
    print(f"Scan time: {results['scan_time']} seconds")
    print(f"Ports scanned: {results['total_ports_scanned']}")
    print(f"Open ports: {results['open_ports']}")
    print(f"{'='*60}")
    
    if results['results']:
        print(f"{'Port':<8} {'Status':<10} {'Service':<20} {'Banner'}")
        print(f"{'-'*60}")
        
        for port in sorted(results['results'].keys()):
            port_info = results['results'][port]
            banner = port_info['banner'] or ''
            if len(banner) > 30:
                banner = banner[:27] + '...'
            
            print(f"{port:<8} {port_info['status']:<10} {port_info['service']:<20} {banner}")
    else:
        print("No open ports found")


def main():
    parser = argparse.ArgumentParser(description='Multithreaded TCP Port Scanner')
    parser.add_argument('target', help='Target IP address or domain name')
    parser.add_argument('-p', '--ports', default='1-1000', 
                       help='Ports to scan (e.g., "80,443" or "1-1000")')
    parser.add_argument('-t', '--timeout', type=float, default=1.0,
                       help='Connection timeout in seconds (default: 1.0)')
    parser.add_argument('-T', '--threads', type=int, default=100,
                       help='Maximum number of threads (default: 100)')
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    parser.add_argument('--no-banner', action='store_true',
                       help='Disable banner grabbing')
    
    args = parser.parse_args()
    
    try:
        scanner = PortScanner(args.target, args.timeout, args.threads)
        
        if args.no_banner:
            scanner._grab_banner = lambda host, port: None
        
        ports = scanner.parse_ports(args.ports)
        print(f"Starting scan of {len(ports)} ports...")
        
        results = scanner.scan_ports(ports)
        display_results(results)
        
        if args.output:
            scanner.save_results(results, args.output)
            
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()