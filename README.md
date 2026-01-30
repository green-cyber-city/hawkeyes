# TCP Port Scanner

A multithreaded TCP port scanner for educational cybersecurity purposes. This tool scans specified ports on a target, identifies open services, and provides banner grabbing capabilities.

## Features

- **Multithreaded Scanning**: Fast concurrent port scanning with configurable thread count
- **Flexible Port Specification**: Support for ranges (1-1000), comma-separated lists (22,80,443), and mixed formats
- **Service Identification**: Automatic identification of common services based on port numbers
- **Banner Grabbing**: Attempts to capture service banners for detailed information
- **Clean Output**: Formatted table display with categorized results
- **JSON Export**: Save scan results to JSON files with metadata
- **Comprehensive Error Handling**: Graceful handling of network errors, timeouts, and user interrupts
- **Educational Focus**: Designed for learning cybersecurity concepts

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TCP-Port-Scanner
```

2. Make the script executable:
```bash
chmod +x main.py
```

## Usage

### Basic Usage

```bash
# Scan common ports on localhost
python3 main.py --target 127.0.0.1 --ports "1-1000"

# Scan specific ports on a website
python3 main.py --target example.com --ports "80,443,8080"

# Fast scan with more threads
python3 main.py --target 192.168.1.1 --ports "1-65535" --threads 200
```

### Command Line Options

- `--target`: Target IP address or domain name (required)
- `--ports`: Ports to scan - supports ranges, lists, and mixed formats (default: "1-1000")
- `--threads`: Number of concurrent threads (default: 100, max: 1000)
- `--timeout`: Connection timeout in seconds (default: 1.0, max: 30)
- `--output`: Optional JSON file to save scan results

### Port Specification Examples

```bash
# Single ports
--ports "80"

# Port ranges
--ports "1-1000"

# Comma-separated lists
--ports "22,80,443,8080"

# Mixed formats
--ports "22,80,443,8000-9000"

# With spaces
--ports "80, 443, 8080"
```

### Output Options

```bash
# Save results to JSON file
python3 main.py --target example.com --ports "1-1000" --output scan_results.json

# Quick summary only
python3 main.py --target example.com --ports "80,443"
```

## Project Structure

```
TCP-Port-Scanner/
├── main.py                 # Main entry point and CLI interface
├── scanner.py              # Core scanning functionality
├── utils/
│   ├── __init__.py
│   ├── port_parser.py       # Port specification parsing
│   ├── services.py          # Service identification
│   ├── banner_grabber.py    # Banner grabbing utilities
│   └── formatter.py         # Result formatting and export
├── tests/                  # Test files (optional)
├── examples/               # Usage examples
└── docs/                   # Documentation
```

## Examples

### Local Development Server Scan

```bash
$ python3 main.py --target 127.0.0.1 --ports "80,443,3306,8080"

TCP Port Scanner Configuration:
  Target: 127.0.0.1
  Ports: 4 ports (80,443,3306,8080)
  Threads: 100
  Timeout: 1.0s

Starting scan...
Port 80/tcp open     HTTP            [HTTP/1.1 200 OK...]
Port 3306/tcp open    MySQL           [8.4.7-0ubuntu0.25.10.3...]

====================================================================================================
SCAN RESULTS FOR 127.0.0.1
====================================================================================================
Target:        127.0.0.1 (127.0.0.1)
Scan time:     0.01 seconds
Ports scanned: 4
Open ports:    2
Success rate:  50.0%
====================================================================================================
Port     Status       Service              Banner
----------------------------------------------------------------------------------------------------
80       open         HTTP                 HTTP/1.1 200 OK...
3306     open         MySQL                8.4.7-0ubuntu0.25.10.3...
====================================================================================================
```

### JSON Output

```json
{
  "target": "example.com",
  "resolved_ip": "93.184.216.34",
  "scan_time": 2.15,
  "total_ports": 1000,
  "open_ports": 2,
  "results": [
    {
      "port": 80,
      "status": "open",
      "service": "HTTP",
      "banner": "HTTP/1.1 200 OK..."
    },
    {
      "port": 443,
      "status": "open",
      "service": "HTTPS",
      "banner": null
    }
  ],
  "scan_metadata": {
    "scanner_version": "1.0.0",
    "timestamp": "2026-01-30T10:52:39.123456",
    "format_version": "1.0"
  }
}
```

## Error Handling

The scanner includes comprehensive error handling for:

- **Invalid targets**: DNS resolution failures, malformed IPs
- **Network errors**: Connection timeouts, unreachable hosts
- **User interruptions**: Clean shutdown on Ctrl+C
- **Resource constraints**: Memory limits, thread cleanup
- **Input validation**: Port ranges, thread counts, timeouts

## Security and Ethics

- **Educational Use Only**: This tool is designed for educational purposes
- **Permission Required**: Only scan targets you own or have permission to scan
- **Rate Limiting**: Be considerate of target systems and network resources
- **Legal Compliance**: Follow all applicable laws and regulations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Educational cybersecurity community
- Python networking documentation
- Open source security tools# tcp-port-scanner
