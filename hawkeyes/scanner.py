#!/usr/bin/env python3

import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from hawkeyes.utils.banner_grabber import BannerGrabber
from hawkeyes.utils.services import get_service_name


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
    
    def __init__(self, timeout: float = 1.0, grab_banners: bool = True):
        self.timeout = timeout
        self.grab_banners = grab_banners
        self.banner_grabber = BannerGrabber()
    
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
                    service_name = get_service_name(port)
                    service = service_name if service_name != "unknown" else "Unknown"
                    banner = (
                        self.banner_grabber.grab_banner(host, port)
                        if self.grab_banners else None
                    )
                    
                    return PortResult(
                        port=port,
                        status='open',
                        service=service,
                        banner=banner
                    )
                else:
                    return PortResult(
                        port=port,
                        status='closed',
                        service=None,
                        banner=None
                    )
                    
        except socket.timeout:
            return PortResult(
                port=port,
                status='filtered',
                service=None,
                banner=None
            )
        except Exception:
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
        
        resolved_ip = self._resolve_target(target)
        results: List[PortResult] = []
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_port = {
                executor.submit(self._scan_single_port, resolved_ip, port): port
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.status == 'open':
                        banner_preview = ""
                        if result.banner:
                            banner_preview = f" [{result.banner[:50]}{'...' if len(result.banner) > 50 else ''}]"
                        print(f"Port {result.port}/tcp {'open':<8} {result.service:<15}{banner_preview}")
                        
                except Exception as e:
                    port = future_to_port[future]
                    print(f"Error scanning port {port}: {e}")
        
        scan_time = time.time() - start_time
        open_count = sum(1 for result in results if result.status == 'open')
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
    test_target = "127.0.0.1"
    test_ports = [22, 80, 443, 8080, 3306]
    
    print(f"Scanning {test_target} on ports {test_ports}...")
    results = scan_target_ports(test_target, test_ports)
    
    print(f"\nScan completed in {results['scan_time']} seconds")
    print(f"Found {results['open_ports']} open ports")
    
    for result in results['results']:
        if result['status'] == 'open':
            print(f"Port {result['port']}: {result['service']} - {result['banner'] or 'No banner'}")
