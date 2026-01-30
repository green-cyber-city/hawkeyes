#!/usr/bin/env python3

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class PortResult:
    """Data class for individual port scan results."""
    port: int
    status: str  # 'open', 'closed', 'filtered'
    service: Optional[str] = None
    banner: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'port': self.port,
            'status': self.status,
            'service': self.service,
            'banner': self.banner
        }


@dataclass
class ScanSummary:
    """Data class for scan summary."""
    target: str
    resolved_ip: str
    scan_time: float
    total_ports: int
    open_ports: int
    results: List[PortResult]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'target': self.target,
            'resolved_ip': self.resolved_ip,
            'scan_time': round(self.scan_time, 2),
            'total_ports': self.total_ports,
            'open_ports': self.open_ports,
            'results': [result.to_dict() for result in self.results]
        }


class TCPPortScanner:
    """Multithreaded TCP port scanner."""
    
    # Common services mapping
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
        5984: 'CouchDB',
        8080: 'HTTP Alternate',
        8443: 'HTTPS Alternate',
        9200: 'Elasticsearch',
        33060: 'MySQL X Protocol',
        54321: 'PostgreSQL Alternate'
    }
    
    def __init__(self, timeout: float = 1.0):
        self.timeout = timeout
        self.lock = threading.Lock()
    
    def _resolve_target(self, target: str) -> str:
        """
        Resolve target hostname or IP address.
        
        Args:
            target: Target hostname or IP address
            
        Returns:
            Resolved IP address
            
        Raises:
            ValueError: If target cannot be resolved
        """
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Cannot resolve hostname: {target}")
    
    def _grab_banner(self, host: str, port: int) -> Optional[str]:
        """
        Attempt to grab service banner from open port.
        
        Args:
            host: Target host IP
            port: Port number to grab banner from
            
        Returns:
            Banner string if available, None otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3.0)  # Longer timeout for banner grabbing
                sock.connect((host, port))
                
                # Send appropriate probe based on port
                probe = self._get_probe_for_port(port)
                if probe:
                    sock.send(probe)
                
                # Try to receive banner
                try:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    return banner[:100] if banner else None
                except:
                    return None
                    
        except:
            return None
    
    def _get_probe_for_port(self, port: int) -> Optional[bytes]:
        """
        Get appropriate probe for banner grabbing based on port.
        
        Args:
            port: Port number
            
        Returns:
            Probe bytes or None if no probe needed
        """
        if port in [80, 8080, 8000, 8008, 8888]:
            return b"GET / HTTP/1.1\r\nHost: target\r\n\r\n"
        elif port in [443, 8443, 9443]:
            return b"GET / HTTP/1.1\r\nHost: target\r\n\r\n"
        elif port == 21:
            return None  # FTP servers usually send banner on connect
        elif port == 22:
            return None  # SSH servers usually send banner on connect
        elif port == 25:
            return None  # SMTP servers usually send banner on connect
        elif port == 110:
            return None  # POP3 servers usually send banner on connect
        elif port == 143:
            return None  # IMAP servers usually send banner on connect
        else:
            return b"HELLO\r\n"
    
    def _scan_single_port(self, host: str, port: int) -> PortResult:
        """
        Scan a single port for status, service, and banner.
        
        Args:
            host: Target host IP
            port: Port number to scan
            
        Returns:
            PortResult object with scan information
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                
                if result == 0:
                    # Port is open
                    status = 'open'
                    service = self.COMMON_SERVICES.get(port, 'Unknown')
                    banner = self._grab_banner(host, port)
                    
                    return PortResult(
                        port=port,
                        status=status,
                        service=service,
                        banner=banner
                    )
                else:
                    # Port is closed
                    return PortResult(
                        port=port,
                        status='closed',
                        service=None,
                        banner=None
                    )
                    
        except socket.timeout:
            # Port is filtered (timeout)
            return PortResult(
                port=port,
                status='filtered',
                service=None,
                banner=None
            )
        except Exception:
            # Other errors, likely filtered
            return PortResult(
                port=port,
                status='filtered',
                service=None,
                banner=None
            )
    
    def scan_ports(self, target: str, ports: List[int], max_threads: int = 100) -> ScanSummary:
        """
        Scan multiple ports on a target using multithreading.
        
        Args:
            target: Target hostname or IP address
            ports: List of ports to scan
            max_threads: Maximum number of concurrent threads
            
        Returns:
            ScanSummary with complete scan results
        """
        start_time = time.time()
        
        # Resolve target
        resolved_ip = self._resolve_target(target)
        
        # Initialize results storage
        results: List[PortResult] = []
        
        # Use ThreadPoolExecutor for concurrent scanning
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all port scanning tasks
            future_to_port = {
                executor.submit(self._scan_single_port, resolved_ip, port): port
                for port in ports
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_port):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Print progress for open ports
                    if result.status == 'open':
                        banner_preview = ""
                        if result.banner:
                            banner_preview = f" [{result.banner[:50]}{'...' if len(result.banner) > 50 else ''}]"
                        print(f"Port {result.port}/tcp {'open':<8} {result.service:<15}{banner_preview}")
                        
                except Exception as e:
                    port = future_to_port[future]
                    print(f"Error scanning port {port}: {e}")
        
        end_time = time.time()
        scan_time = end_time - start_time
        
        # Count open ports
        open_count = sum(1 for result in results if result.status == 'open')
        
        # Sort results by port number
        results.sort(key=lambda x: x.port)
        
        return ScanSummary(
            target=target,
            resolved_ip=resolved_ip,
            scan_time=scan_time,
            total_ports=len(ports),
            open_ports=open_count,
            results=results
        )


def scan_target_ports(target: str, ports: List[int], timeout: float = 1.0, 
                     max_threads: int = 100) -> Dict[str, Any]:
    """
    Convenience function to scan ports on a target.
    
    Args:
        target: Target hostname or IP address
        ports: List of ports to scan
        timeout: Connection timeout in seconds
        max_threads: Maximum number of concurrent threads
        
    Returns:
        Dictionary with scan results
    """
    scanner = TCPPortScanner(timeout=timeout)
    summary = scanner.scan_ports(target, ports, max_threads)
    return summary.to_dict()


if __name__ == "__main__":
    # Simple test
    test_target = "127.0.0.1"
    test_ports = [22, 80, 443, 8080, 3306]
    
    print(f"Scanning {test_target} on ports {test_ports}...")
    results = scan_target_ports(test_target, test_ports)
    
    print(f"\nScan completed in {results['scan_time']} seconds")
    print(f"Found {results['open_ports']} open ports")
    
    for result in results['results']:
        if result['status'] == 'open':
            print(f"Port {result['port']}: {result['service']} - {result['banner'] or 'No banner'}")