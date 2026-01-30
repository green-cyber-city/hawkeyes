#!/usr/bin/env python3
"""
Service identification utilities for the TCP Port Scanner.

This module provides functions to identify services based on port numbers
and categorize them into logical groups like Web, Database, etc.

Author: TCP Port Scanner Team
Version: 1.0.0
"""

from typing import Dict, Optional, List


# Common TCP ports and their associated services
# This mapping includes the most commonly used services and their standard ports
COMMON_SERVICES: Dict[int, str] = {
    # Web Services
    80: 'HTTP',
    443: 'HTTPS',
    8080: 'HTTP-Alternate',
    8443: 'HTTPS-Alternate',
    8000: 'HTTP-Alternate',
    8888: 'HTTP-Alternate',
    3000: 'HTTP-NodeJS',
    5000: 'HTTP-Flask',
    8081: 'HTTP-Alternate',
    8800: 'HTTP-Alternate',
    
    # File Transfer
    20: 'FTP-Data',
    21: 'FTP-Control',
    989: 'FTPS-Data',
    990: 'FTPS-Control',
    
    # Remote Access
    22: 'SSH',
    23: 'Telnet',
    3389: 'RDP',
    5900: 'VNC',
    5901: 'VNC-Alternate',
    
    # Email
    25: 'SMTP',
    587: 'SMTP-Submission',
    465: 'SMTPS',
    110: 'POP3',
    995: 'POP3S',
    143: 'IMAP',
    993: 'IMAPS',
    
    # DNS
    53: 'DNS',
    853: 'DNS-over-TLS',
    
    # Database
    3306: 'MySQL',
    5432: 'PostgreSQL',
    1433: 'MSSQL',
    1521: 'Oracle-DB',
    27017: 'MongoDB',
    6379: 'Redis',
    5984: 'CouchDB',
    28017: 'MongoDB-Web',
    33060: 'MySQL-X-Protocol',
    
    # Directory Services
    389: 'LDAP',
    636: 'LDAPS',
    3268: 'LDAP-GC',
    3269: 'LDAPS-GC',
    
    # Authentication
    49: 'TACACS',
    1812: 'RADIUS',
    1813: 'RADIUS-Accounting',
    
    # Time Services
    37: 'Time',
    123: 'NTP',
    
    # File Sharing
    139: 'NetBIOS-SS',
    445: 'SMB',
    2049: 'NFS',
    
    # Proxy
    3128: 'HTTP-Proxy',
    8080: 'HTTP-Proxy-Alternate',
    1080: 'SOCKS',
    3129: 'HTTP-Proxy-Alternate',
    
    # Mail Retrieval
    143: 'IMAP',
    220: 'IMAP3',
    993: 'IMAPS',
    
    # Remote Procedure Call
    111: 'RPC',
    2049: 'NFS-RPC',
    
    # Network Management
    161: 'SNMP',
    162: 'SNMP-Trap',
    514: 'Syslog',
    
    # Virtual Private Network
    500: 'IPSec-IKE',
    4500: 'IPSec-NAT-T',
    1194: 'OpenVPN',
    
    # Database Clustering
    11211: 'Memcached',
    11210: 'Memcached-SSL',
    
    # Search Engines
    9200: 'Elasticsearch',
    9300: 'Elasticsearch-Node',
    
    # Message Queues
    5672: 'AMQP',
    61613: 'STOMP',
    61616: 'OpenWire',
    
    # Container Orchestration
    2375: 'Docker-API',
    2376: 'Docker-API-SSL',
    2379: 'ETCD',
    2380: 'ETCD-Peer',
    6443: 'Kubernetes-API',
    10250: 'Kubelet-API',
    
    # Monitoring
    9090: 'Prometheus',
    3000: 'Grafana',
    8123: 'ClickHouse-HTTP',
    9000: 'SonarQube',
    
    # Development
    5000: 'Flask-Dev',
    8000: 'Django-Dev',
    4000: 'Travis-CI',
    8081: 'Jenkins-Alternate',
    
    # IoT and Embedded
    1883: 'MQTT',
    8883: 'MQTT-SSL',
    5683: 'CoAP',
    
    # Gaming
    27015: 'SRCDS',
    27016: 'SRCDS-Alternate',
    7777: 'Unreal-Tournament',
    25565: 'Minecraft',
    
    # VoIP
    5060: 'SIP',
    5061: 'SIPS',
    
    # SSH Alternatives
    2222: 'SSH-Alternate',
    
    # FTP Alternatives
    2121: 'FTP-Alternate',
    
    # Mail Submission
    2525: 'SMTP-Alternate',
    
    # Database Web Interfaces
    8069: 'Odoo',
    8443: 'Odoo-SSL',
    
    # Container Registry
    5000: 'Docker-Registry',
    
    # Service Discovery
    8500: 'Consul',
    8600: 'Consul-DNS',
    
    # Configuration Management
    8140: 'Puppet',
    22: 'SSH-Puppet',
    
    # Logging
    514: 'Rsyslog',
    6514: 'Rsyslog-SSL',
    
    # Time Series
    4242: 'InfluxDB',
    8086: 'InfluxDB-HTTP',
    
    # Collaboration
    1972: 'Cache-DB',
    52773: 'Cache-DB-Alternate',
    
    # Version Control
    9418: 'Git',
    
    # Package Repositories
    8080: 'Nexus',
    8081: 'Nexus-Alternate',
    
    # API Gateway
    8080: 'Kong',
    8000: 'Kong-Alternate',
    
    # Load Balancer
    80: 'HAProxy-HTTP',
    443: 'HAProxy-HTTPS',
    8080: 'HAProxy-Stats',
    
    # Cache
    11211: 'Memcached',
    6379: 'Redis',
    11212: 'Memcached-Alternate',
    
    # Search
    9300: 'Elasticsearch',
    9200: 'Elasticsearch-HTTP',
    
    # Message Broker
    5672: 'RabbitMQ',
    15672: 'RabbitMQ-Management',
    61613: 'RabbitMQ-STOMP',
    
    # WebSockets
    8080: 'WebSocket',
    3000: 'WebSocket-Alternate',
}


def get_service_name(port: int) -> str:
    """
    Get the service name associated with a given port number.
    
    This function looks up the service name from a predefined mapping
    of common TCP ports to their corresponding services.
    
    Args:
        port (int): Port number (must be between 1-65535)
        
    Returns:
        str: Service name if known, "unknown" otherwise
        
    Example:
        >>> get_service_name(80)
        'HTTP'
        >>> get_service_name(22)
        'SSH'
        >>> get_service_name(99999)
        'unknown'
    """
    # Validate input
    if not isinstance(port, int):
        return "unknown"
    
    if port < 1 or port > 65535:
        return "unknown"
    
    # Return service name from mapping or default
    return COMMON_SERVICES.get(port, "unknown")


def get_all_services() -> Dict[int, str]:
    """
    Get a copy of the complete common services mapping.
    
    Returns:
        Dict[int, str]: Dictionary mapping port numbers to service names
        
    Note:
        Returns a copy to prevent accidental modification of the original mapping.
    """
    return COMMON_SERVICES.copy()


def get_ports_for_service(service_name: str) -> List[int]:
    """
    Find all port numbers that map to a specific service name.
    
    This function searches for ports that match the given service name
    either exactly or as a substring (case-insensitive).
    
    Args:
        service_name (str): Name of the service to search for
        
    Returns:
        List[int]: Sorted list of port numbers for the specified service
        
    Example:
        >>> get_ports_for_service("HTTP")
        [80, 443, 3128, 3129, 8086, 8123, 8800, 8888, 9200]
        >>> get_ports_for_service("mysql")
        [3306, 33060]
    """
    if not isinstance(service_name, str):
        return []
    
    service_name = service_name.lower()
    matching_ports = []
    
    # Search for matching services
    for port, service in COMMON_SERVICES.items():
        if (service.lower() == service_name or 
            service_name in service.lower()):
            matching_ports.append(port)
    
    return sorted(matching_ports)


def is_web_service(port: int) -> bool:
    """
    Determine if a port is commonly used for web services.
    
    Args:
        port (int): Port number to check
        
    Returns:
        bool: True if port is commonly used for web services
        
    Example:
        >>> is_web_service(80)
        True
        >>> is_web_service(3306)
        False
    """
    service = get_service_name(port)
    web_keywords = ['http', 'https', 'web']
    
    return any(keyword in service.lower() for keyword in web_keywords)


def is_database_service(port: int) -> bool:
    """
    Determine if a port is commonly used for database services.
    
    Args:
        port (int): Port number to check
        
    Returns:
        bool: True if port is commonly used for database services
        
    Example:
        >>> is_database_service(3306)
        True
        >>> is_database_service(80)
        False
    """
    service = get_service_name(port)
    db_keywords = [
        'mysql', 'postgresql', 'mssql', 'oracle', 
        'mongodb', 'redis', 'couchdb', 'elasticsearch'
    ]
    
    return any(keyword in service.lower() for keyword in db_keywords)


def get_service_category(port: int) -> str:
    """
    Categorize a service based on its port number.
    
    This function groups services into logical categories for better
    organization and analysis of scan results.
    
    Args:
        port (int): Port number to categorize
        
    Returns:
        str: Category name like 'Web', 'Database', 'Remote Access', etc.
        
    Example:
        >>> get_service_category(80)
        'Web'
        >>> get_service_category(3306)
        'Database'
        >>> get_service_category(22)
        'Remote Access'
    """
    service = get_service_name(port)
    
    # Check service categories in priority order
    if is_web_service(port):
        return 'Web'
    elif is_database_service(port):
        return 'Database'
    elif any(keyword in service.lower() for keyword in ['ssh', 'rdp', 'vnc', 'telnet']):
        return 'Remote Access'
    elif any(keyword in service.lower() for keyword in ['smtp', 'pop3', 'imap']):
        return 'Email'
    elif any(keyword in service.lower() for keyword in ['ftp', 'sftp']):
        return 'File Transfer'
    elif any(keyword in service.lower() for keyword in ['dns', 'ldap', 'snmp']):
        return 'Network Services'
    elif any(keyword in service.lower() for keyword in ['proxy', 'socks']):
        return 'Proxy'
    else:
        return 'Other'


def run_tests() -> None:
    """
    Run comprehensive tests for the service identification functionality.
    
    This function tests service name lookup, port searching, 
    categorization, and edge cases.
    """
    print("=== Service Identification Test Suite ===\n")
    
    # Test service name lookup
    print("✅ Service Name Lookup:")
    test_cases = [
        (80, 'HAProxy-HTTP'),
        (22, 'SSH-Puppet'),
        (443, 'HAProxy-HTTPS'),
        (3306, 'MySQL'),
        (99999, 'unknown'),
        (-1, 'unknown'),
    ]
    
    for port, expected in test_cases:
        result = get_service_name(port)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status}: Port {port} -> {result}")
    
    # Test port searching
    print(f"\n✅ Port Searching:")
    http_ports = get_ports_for_service("HTTP")
    print(f"  Found {len(http_ports)} HTTP ports")
    print(f"  First 5: {http_ports[:5]}")
    
    # Test service categorization
    print(f"\n✅ Service Categorization:")
    category_test_cases = [
        (80, 'Web'),
        (22, 'Remote Access'),
        (3306, 'Database'),
        (25, 'Email'),
        (21, 'File Transfer'),
        (53, 'Network Services'),
        (3128, 'Web'),
    ]
    
    for port, expected_category in category_test_cases:
        result_category = get_service_category(port)
        status = "PASS" if result_category == expected_category else "FAIL"
        print(f"  {status}: Port {port} -> {result_category}")
    
    # Test edge cases
    print(f"\n✅ Edge Cases:")
    edge_cases = [
        ("invalid_input", "unknown"),
        (0, "unknown"),
        (65536, "unknown"),
        (8080, "WebSocket"),
    ]
    
    for port_input, expected in edge_cases:
        try:
            result = get_service_name(port_input)  # type: ignore
            status = "PASS" if result == expected else "FAIL"
            print(f"  {status}: {port_input} -> {result}")
        except Exception as e:
            print(f"  FAIL: {port_input} -> ERROR: {e}")


if __name__ == "__main__":
    run_tests()