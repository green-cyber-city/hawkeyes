#!/usr/bin/env python3

import socket
from typing import Optional, Tuple


class BannerGrabber:
    """Utility class for grabbing service banners from open ports."""
    
    def __init__(self, timeout: float = 3.0, max_banner_length: int = 200):
        """
        Initialize banner grabber.
        
        Args:
            timeout: Socket timeout for banner grabbing (seconds)
            max_banner_length: Maximum length of banner to return
        """
        self.timeout = timeout
        self.max_banner_length = max_banner_length
        
        # Port-specific probes for better banner grabbing
        self.probes = {
            # HTTP/HTTPS services
            80: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            443: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            8080: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            8443: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            8000: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            8888: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            3000: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            5000: b"GET / HTTP/1.1\r\nHost: target\r\nUser-Agent: Scanner/1.0\r\n\r\n",
            
            # FTP - No probe needed, servers send banner on connect
            21: None,
            2121: None,  # FTP alternate
            
            # SSH - No probe needed, servers send banner on connect
            22: None,
            2222: None,  # SSH alternate
            
            # SMTP - No probe needed, servers send banner on connect
            25: None,
            587: None,  # SMTP submission
            465: None,  # SMTPS
            
            # POP3 - No probe needed, servers send banner on connect
            110: None,
            995: None,  # POP3S
            
            # IMAP - No probe needed, servers send banner on connect
            143: None,
            993: None,  # IMAPS
            
            # Telnet - No probe needed, servers send banner on connect
            23: None,
            
            # Database services
            3306: None,  # MySQL sends banner on connect
            5432: None,  # PostgreSQL
            1433: None,  # MSSQL
            1521: None,  # Oracle
            27017: None,  # MongoDB
            
            # LDAP
            389: None,
            636: None,  # LDAPS
            
            # Simple probes for other common services
            53: b"",  # DNS - empty probe
            161: b"",  # SNMP
            135: None,  # RPC
            139: None,  # NetBIOS
            445: None,  # SMB
            
            # Default probe for unknown ports
            'default': b"HELLO\r\n"
        }
    
    def _get_probe_for_port(self, port: int) -> Optional[bytes]:
        """
        Get the appropriate probe for a specific port.
        
        Args:
            port: Port number
            
        Returns:
            Probe bytes or None if no probe needed
        """
        return self.probes.get(port, self.probes['default'])
    
    def _clean_banner(self, banner: bytes) -> str:
        """
        Clean and decode banner bytes to string.
        
        Args:
            banner: Raw banner bytes
            
        Returns:
            Cleaned banner string
        """
        try:
            # Try UTF-8 first
            decoded = banner.decode('utf-8', errors='ignore')
        except:
            try:
                # Fallback to Latin-1
                decoded = banner.decode('latin-1', errors='ignore')
            except:
                # Last resort - replace non-printable chars
                decoded = ''.join(chr(b) if 32 <= b <= 126 else '?' for b in banner[:100])
        
        # Remove excessive whitespace and control characters
        cleaned = ''.join(char for char in decoded if char.isprintable() or char in ['\n', '\r', '\t'])
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Limit length
        if len(cleaned) > self.max_banner_length:
            cleaned = cleaned[:self.max_banner_length] + '...'
        
        return cleaned
    
    def grab_banner(self, host: str, port: int) -> Optional[str]:
        """
        Attempt to grab service banner from an open port.
        
        Args:
            host: Target host IP address
            port: Open port number
            
        Returns:
            Banner string if successful, None otherwise
        """
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Connect to the port
            sock.connect((host, port))
            
            probe = self._get_probe_for_port(port)
            banner_data = b""
            
            if probe is None:
                # Services like SSH/FTP/SMTP send a banner on connect
                try:
                    banner_data = sock.recv(1024)
                except socket.timeout:
                    pass
            else:
                if probe:
                    try:
                        sock.send(probe)
                    except Exception:
                        pass
                try:
                    banner_data = sock.recv(1024)
                except socket.timeout:
                    pass
            
            sock.close()
            
            # Process banner data
            if banner_data:
                cleaned_banner = self._clean_banner(banner_data)
                return cleaned_banner if cleaned_banner else None
            
            return None
            
        except socket.timeout:
            # Connection timeout - likely filtered or slow service
            return None
        except ConnectionRefusedError:
            # Connection refused - port closed
            return None
        except socket.gaierror:
            # Host resolution error
            return None
        except OSError:
            # Network-related error
            return None
        except Exception:
            # Any other unexpected error
            return None
    
    def grab_banner_with_details(self, host: str, port: int) -> Tuple[Optional[str], str]:
        """
        Grab banner with additional error information.
        
        Args:
            host: Target host IP address
            port: Open port number
            
        Returns:
            Tuple of (banner, status_message)
        """
        try:
            banner = self.grab_banner(host, port)
            if banner:
                return banner, "success"
            else:
                return None, "no_banner"
                
        except socket.timeout:
            return None, "timeout"
        except ConnectionRefusedError:
            return None, "connection_refused"
        except socket.gaierror as e:
            return None, f"host_error: {e}"
        except OSError as e:
            return None, f"network_error: {e}"
        except Exception as e:
            return None, f"unexpected_error: {e}"


def grab_banner_simple(host: str, port: int, timeout: float = 3.0) -> Optional[str]:
    """
    Simple banner grabbing function.
    
    Args:
        host: Target host IP address
        port: Open port number
        timeout: Connection timeout in seconds
        
    Returns:
        Banner string if successful, None otherwise
    """
    grabber = BannerGrabber(timeout=timeout)
    return grabber.grab_banner(host, port)


# Test function
if __name__ == "__main__":
    test_targets = [
        ("127.0.0.1", 80),    # HTTP
        ("127.0.0.1", 22),    # SSH
        ("127.0.0.1", 3306),  # MySQL
        ("127.0.0.1", 443),   # HTTPS
        ("127.0.0.1", 25),    # SMTP
        ("127.0.0.1", 9999),  # Likely closed
    ]
    
    print("=== Banner Grabbing Test ===")
    
    grabber = BannerGrabber()
    
    for host, port in test_targets:
        print(f"\nTesting {host}:{port}")
        banner, status = grabber.grab_banner_with_details(host, port)
        
        if banner:
            print(f"  Status: {status}")
            print(f"  Banner: {banner}")
        else:
            print(f"  Status: {status}")
            print(f"  Banner: No banner captured")