# TCP Port Scanner - User Guide

A comprehensive guide to using the TCP Port Scanner for educational cybersecurity purposes.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Command Line Options](#command-line-options)
4. [Port Specification](#port-specification)
5. [Usage Examples](#usage-examples)
6. [Output Formats](#output-formats)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Educational Use Cases](#educational-use-cases)

## Installation

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Setup Steps

1. **Download/Clone the Scanner:**
```bash
# If cloning from repository
git clone <repository-url>
cd TCP-Port-Scanner

# Or download the files directly
```

2. **Make the Script Executable:**
```bash
chmod +x main.py
```

3. **Verify Installation:**
```bash
python3 main.py --help
```

You should see the help message with all available options.

## Quick Start

### Basic Scan
```bash
# Scan the first 1000 ports on localhost
python3 main.py --target 127.0.0.1 --ports "1-1000"
```

### Scan a Website
```bash
# Scan common web ports on a website
python3 main.py --target example.com --ports "80,443,8080"
```

### Save Results
```bash
# Save scan results to a JSON file
python3 main.py --target example.com --ports "1-1000" --output results.json
```

## Command Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--target` | Yes | - | Target IP address or domain name |
| `--ports` | No | "1-1000" | Ports to scan (ranges, lists, or mixed) |
| `--threads` | No | 100 | Number of concurrent threads (max: 1000) |
| `--timeout` | No | 1.0 | Connection timeout in seconds (max: 30) |
| `--output` | No | - | JSON file to save scan results |

### Option Details

#### --target
Specifies the target to scan:
- **IP Address**: `192.168.1.1`, `127.0.0.1`
- **Domain Name**: `example.com`, `google.com`
- **Hostname**: `server.local`

#### --ports
Specifies which ports to scan:
```bash
--ports "80"                    # Single port
--ports "1-1000"               # Port range
--ports "22,80,443"            # Comma-separated list
--ports "22,80,443,8000-9000"  # Mixed format
--ports " 80 , 443 , 8080 "     # With spaces
```

#### --threads
Controls scanning speed:
```bash
--threads 50    # Slower, less aggressive
--threads 100   # Default balanced speed
--threads 200   # Fast scan
--threads 500   # Very aggressive
```

#### --timeout
Controls connection wait time:
```bash
--timeout 0.5   # Fast scan, may miss slow services
--timeout 1.0    # Default balanced
--timeout 2.0    # More reliable, slower
--timeout 5.0    # Very thorough
```

#### --output
Saves detailed scan results:
```bash
--output scan_results.json    # Save to current directory
--output /path/to/scan.json   # Save to specific location
```

## Port Specification

### Supported Formats

#### Single Ports
```bash
--ports "80"
--ports "443"
--ports "22"
```

#### Port Ranges
```bash
--ports "1-1000"       # Ports 1 through 1000
--ports "8000-9000"     # Ports 8000 through 9000
--ports "1-65535"       # All possible ports (very slow)
```

#### Comma-Separated Lists
```bash
--ports "22,80,443"                    # SSH, HTTP, HTTPS
--ports "80,8080,8000,8888"           # Multiple web ports
--ports "21,22,23,25,53,80,110,143"   # Common services
```

#### Mixed Formats
```bash
--ports "22,80,443,8000-9000,3306"     # Mixed single ports and ranges
--ports "1-100,200-300,400"           # Multiple ranges
```

#### With Spaces
```bash
--ports "80, 443, 8080"               # Spaces are ignored
--ports "1 - 1000"                    # Spaces around hyphen
```

### Limits and Validations

- **Port Range**: 1-65535 (valid TCP ports)
- **Maximum Range Size**: 10,000 ports per range
- **Character Validation**: Only numbers, commas, hyphens, and spaces allowed
- **No Empty Specifications**: Empty strings or spaces are rejected

## Usage Examples

### Basic Scanning

#### Scan Localhost
```bash
# Scan common development ports
python3 main.py --target 127.0.0.1 --ports "80,443,3000,5000,8080"

# Scan first 1000 ports
python3 main.py --target 127.0.0.1 --ports "1-1000"
```

#### Scan Remote Servers
```bash
# Scan web server
python3 main.py --target example.com --ports "80,443,8080,8443"

# Scan all common ports
python3 main.py --target 192.168.1.1 --ports "21,22,23,25,53,80,110,143,443,993,995"
```

### Advanced Scanning

#### High-Speed Scanning
```bash
# Fast scan with more threads
python3 main.py --target example.com --ports "1-1000" --threads 200 --timeout 0.5

# Very aggressive scan
python3 main.py --target example.com --ports "1-1000" --threads 500 --timeout 0.3
```

#### Thorough Scanning
```bash
# Slow, thorough scan
python3 main.py --target example.com --ports "1-1000" --threads 50 --timeout 2.0

# Full port scan (very slow)
python3 main.py --target example.com --ports "1-65535" --threads 100 --timeout 3.0
```

### Educational Scenarios

#### Learning Web Services
```bash
# Find web servers on a network
python3 main.py --target 192.168.1.0/24 --ports "80,443,8080,8443,3000,5000"
```

#### Database Discovery
```bash
# Scan for common database ports
python3 main.py --target database-server.local --ports "3306,5432,1433,1521,27017,6379"
```

#### Remote Access Services
```bash
# Find remote access services
python3 main.py --target 192.168.1.1 --ports "22,23,3389,5900,5901"
```

### Batch Scanning

#### Multiple Targets Script
```bash
#!/bin/bash
# scan_network.sh

targets=("192.168.1.1" "192.168.1.2" "192.168.1.3")
ports="22,80,443,3389"

for target in "${targets[@]}"; do
    echo "Scanning $target..."
    python3 main.py --target "$target" --ports "$ports" --output "scan_$target.json"
    echo "Done with $target"
done
```

#### Common Ports Scan
```bash
# Scan only the most common 100 ports
common_ports="1,7,9,13,17,19,20,21,22,23,25,26,30,32,33,37,42,43,49,53,67,68,69,70,71,79,80,81,82,83,84,85,88,89,90,99,100,106,109,110,111,113,119,125,135,139,143,144,161,162,163,164,165,179,199,211,212,213,214,223,254,255,256,259,264,280,301,306,311,340,366,389,401,406,411,427,443,444,445,458,464,465,481,497,500,512,513,514,515,517,518,523,526,530,531,532,533,540,542,543,544,545,546,548,554,556,560,561,563,564,567,569,570,571,573,577,587,593,595,596,597,600,601,604,617,623,625,631,636,639,646,647,648,652,654,657,666,674,678,683,687,691,695,698,699,700,701,702,706,711,712,714,720,726,749,765,777,783,787,800,801,808,843,873,880,888,898,900,901,902,903,911,912,981,987,990,992,993,995,999,1000,1001,1002,1007,1009,1010,1011,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,1097,1098,1099,1100"

python3 main.py --target example.com --ports "$common_ports" --output common_ports_scan.json
```

## Output Formats

### Console Output

#### Summary Information
```
TCP Port Scanner Configuration:
  Target: example.com
  Ports: 1000 ports (1-1000)
  Threads: 100
  Timeout: 1.0s
  Output: scan_results.json

Starting scan...
Port 80/tcp open     HTTP            [HTTP/1.1 200 OK...]
Port 443/tcp open    HTTPS           [SSL handshake...]
```

#### Results Table
```
====================================================================================================
SCAN RESULTS FOR EXAMPLE.COM
====================================================================================================
Target:        example.com (93.184.216.34)
Scan time:     2.15 seconds
Ports scanned: 1000
Open ports:     2
Success rate:   0.2%
====================================================================================================
Port     Status       Service              Banner
----------------------------------------------------------------------------------------------------
80       open         HTTP                 HTTP/1.1 200 OK...
443      open         HTTPS                SSL handshake...
====================================================================================================
```

### JSON Output

#### Structure
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
      "banner": "HTTP/1.1 200 OK\r\n..."
    },
    {
      "port": 443,
      "status": "open",
      "service": "HTTPS",
      "banner": "SSL handshake..."
    }
  ],
  "scan_metadata": {
    "scanner_version": "1.0.0",
    "timestamp": "2026-01-30T10:52:39.123456",
    "format_version": "1.0"
  }
}
```

#### Field Descriptions

| Field | Description |
|--------|-------------|
| `target` | Original target specified by user |
| `resolved_ip` | Resolved IP address |
| `scan_time` | Time taken in seconds |
| `total_ports` | Number of ports scanned |
| `open_ports` | Count of open ports found |
| `results` | Array of port scan results |
| `port` | Port number |
| `status` | "open", "closed", or "filtered" |
| `service` | Identified service name |
| `banner` | Captured service banner (if available) |

## Error Handling

### Common Errors and Solutions

#### DNS Resolution Errors
```bash
Error: DNS resolution failed: Unable to resolve hostname 'invalid-domain'
Solution: Check the target hostname or use an IP address directly
```

#### Network Connectivity Errors
```bash
Error: Network error: No route to host '192.168.1.100'
Solution: Check network connectivity and target accessibility
```

#### Permission Errors
```bash
Error: Permission denied
Solution: Try with sudo or check firewall settings
```

#### Timeout Errors
```bash
Error: Connection timeout: Target is not responding within 1.0s
Solution: Increase timeout with --timeout parameter
```

#### Invalid Input Errors
```bash
Error: Port specification error: Port range too large (max 10000 ports): 1-50000
Solution: Use smaller ranges or break into multiple scans
```

### Graceful Shutdown

The scanner handles interruptions cleanly:

#### Ctrl+C Handling
```bash
$ python3 main.py --target example.com --ports "1-1000"
Starting scan...
^C⚠ Scan interrupted by user. Cleaning up...
```

#### Network Timeouts
```bash
$ python3 main.py --target 192.0.2.1 --ports "1-1000" --timeout 0.5
Starting scan...
(Network continues, but adapts to timeouts)
```

## Best Practices

### Scanning Etiquette

#### 1. Get Permission
- Only scan targets you own or have explicit permission to scan
- Use in authorized penetration testing environments only
- Follow organizational security policies

#### 2. Rate Limiting
```bash
# Responsible scanning
python3 main.py --target example.com --ports "1-1000" --threads 50 --timeout 2.0

# Avoid aggressive scanning
# Don't use: --threads 1000 --timeout 0.1
```

#### 3. Network Impact
```bash
# Lower impact scanning
python3 main.py --target example.com --ports "1-1000" --threads 25 --timeout 3.0

# Avoid network congestion
# Don't scan entire /24 networks with high thread counts
```

### Performance Optimization

#### 1. Thread Tuning
```bash
# Slow networks
--threads 25 --timeout 3.0

# Fast networks
--threads 200 --timeout 1.0

# Local scanning
--threads 100 --timeout 0.5
```

#### 2. Port Selection
```bash
# Quick assessment
--ports "22,80,443,3389"

# Common services
--ports "1-1000"

# Comprehensive
--ports "1-65535"  # Use with caution
```

#### 3. Timeout Optimization
```bash
# Local/quick scanning
--timeout 0.5

# Internet scanning
--timeout 2.0

# Unreliable networks
--timeout 5.0
```

### Result Management

#### 1. File Naming
```bash
# Descriptive filenames
--output "scan_example_com_$(date +%Y%m%d_%H%M%S).json"
--output "network_192.168.1.0_24_common_ports.json"
```

#### 2. Organized Structure
```bash
# Organize scans by target
mkdir -p scans/example.com
python3 main.py --target example.com --ports "1-1000" --output "scans/example.com/full_scan.json"

# Organize by date
mkdir -p scans/$(date +%Y-%m-%d)
python3 main.py --target example.com --ports "1-1000" --output "scans/$(date +%Y-%m-%d)/example.json"
```

## Troubleshooting

### Performance Issues

#### Slow Scanning
```bash
# Symptoms: Scan takes very long
# Solutions:
--threads 200          # Increase threads
--timeout 0.5          # Reduce timeout
--ports "80,443"       # Scan fewer ports
```

#### High Memory Usage
```bash
# Symptoms: Out of memory errors
# Solutions:
--ports "1-5000"       # Reduce port range
--threads 50           # Reduce threads
```

#### Network Timeouts
```bash
# Symptoms: Many timeout errors
# Solutions:
--timeout 5.0          # Increase timeout
--threads 25           # Reduce threads for less network load
```

### Common Problems

#### 1. Permission Denied
```bash
# Problem: Permission denied for ports < 1024
# Solutions:
sudo python3 main.py --target localhost --ports "1-1024"
# or scan only high ports
--ports "1025-65535"
```

#### 2. Host Not Found
```bash
# Problem: DNS resolution fails
# Solutions:
# Use IP address directly
--target 192.168.1.1

# Check DNS
nslookup example.com
```

#### 3. No Results
```bash
# Problem: Scan completes but shows no open ports
# Solutions:
# Increase timeout
--timeout 5.0

# Check connectivity
ping target_ip

# Try specific ports you know are open
--ports "80"
```

### Debug Mode

#### Verbose Scanning
```bash
# Enable progress indicators
python3 main.py --target example.com --ports "80,443" --threads 1

# Watch for real-time results
# Open ports are printed as they're found
```

## Educational Use Cases

### 1. Network Services Discovery

#### Learning Web Services
```bash
# Find different types of web servers
python3 main.py --target lab-server.local --ports "80,443,8080,8443,3000,5000,8000"

# Learn about different web technologies
python3 main.py --target example.com --ports "80,443" --output web_analysis.json
```

#### Database Services
```bash
# Identify database systems
python3 main.py --target database-server.local --ports "3306,5432,1433,1521,27017,6379"

# Learn database banner information
python3 main.py --target mysql-server.local --ports "3306" --timeout 5.0
```

### 2. Security Assessment Learning

#### Service Enumeration
```bash
# Learn service enumeration
python3 main.py --target target.local --ports "1-1000" --output service_enum.json

# Analyze results to understand:
# - Which services are running
# - Service versions from banners
# - Potential security implications
```

#### Banner Analysis
```bash
# Learn to read service banners
python3 main.py --target ftp-server.local --ports "21" --timeout 3.0

# Common banner formats:
# FTP: "220 (vsFTPd 3.0.3)"
# SSH: "SSH-2.0-OpenSSH_8.2p1"
# HTTP: "HTTP/1.1 200 OK"
```

### 3. Network Protocols Study

#### Protocol Identification
```bash
# Study different network protocols
python3 main.py --target lab-server.local --ports "22,23,25,53,80,110,143,443"

# Analyze banners to understand:
# - Protocol versions
# - Server software
# - Configuration details
```

### 4. Cybersecurity Lab Exercises

#### Port Scanning Labs
```bash
# Exercise 1: Basic scanning
python3 main.py --target lab-vm.local --ports "1-1000"

# Exercise 2: Service identification
python3 main.py --target lab-vm.local --ports "1-1000" --output lab_services.json

# Exercise 3: Banner grabbing
python3 main.py --target lab-vm.local --ports "22,80,443" --timeout 5.0
```

#### Vulnerability Assessment Prep
```bash
# Practice vulnerability assessment workflow
# Step 1: Discover open ports
python3 main.py --target target.local --ports "1-65535" --output discovery.json

# Step 2: Analyze services
# (Manual analysis of discovery.json)

# Step 3: Research vulnerabilities
# (External research based on service versions)
```

### 5. Programming Learning

#### Understanding Network Programming
```bash
# Learn how TCP connections work
# Study the scanner source code in scanner.py
# Understand socket programming concepts

# Test connection behavior
python3 main.py --target target.local --ports "80" --threads 1
```

#### Multithreading Concepts
```bash
# Learn about concurrent programming
# Experiment with different thread counts
--threads 1      # Sequential scanning
--threads 50     # Moderate concurrency
--threads 200    # High concurrency

# Observe performance differences
```

---

## Safety and Legal Notice

**⚠️ IMPORTANT:**
- This tool is for **educational purposes only**
- **Never scan targets without explicit permission**
- Follow all applicable laws and regulations
- Use only in authorized testing environments
- Be respectful of network resources

## Support

For issues, questions, or contributions:
- Check the [README.md](README.md) for general information
- Review this guide for usage instructions
- Examine the source code for technical details
- Test with known targets before production use

Happy learning and stay safe! 🚀