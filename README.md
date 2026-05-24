# Hawkeyes

A multithreaded TCP port scanner for educational cybersecurity. Hawkeyes scans TCP ports, identifies open services, and grabs banners.

> **Authorized use only.** Only scan systems you own or have explicit permission to test.

## Install (Linux)

No Python. No pip. One command:

```bash
curl -fsSL https://github.com/kyawyelin284/tcp-port-scanner/releases/download/v1.0.0/install.sh | sh
```

This downloads a standalone `hawk` binary and installs it to `~/.local/bin/hawk`.

**Requirements:** Linux (x86_64 or ARM64) and `curl` or `wget`.

If `~/.local/bin` is not in your PATH, the installer prints the line to add to `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="${PATH}:$HOME/.local/bin"
```

## Quick start

```bash
hawk
hawk target example.com --ports "80,443"
```

## Usage

### Show banner and help

```bash
hawk
```

### Scan a target

```bash
hawk target example.com --ports "80,443"
hawk target 127.0.0.1 --ports "1-1000"
hawk target 192.168.1.1 --ports "22,80,443,8080" --threads 200 --timeout 2.0
hawk target example.com --ports "80,443" --output scan_results.json
```

### Command reference

```
hawk                          Show banner and usage info
hawk target HOST [options]    Scan TCP ports on a target

Options:
  --ports PORTS     Ports to scan (default: "1-1000")
  --threads N       Concurrent threads (default: 100, max: 1000)
  --timeout SECS    Connection timeout in seconds (default: 1.0, max: 30)
  --output FILE     Save results to a JSON file
  --version         Show version
```

### Port specification examples

```bash
--ports "80"
--ports "1-1000"
--ports "22,80,443,8080"
--ports "22,80,443,8000-9000"
```

## Features

- **Multithreaded scanning** with configurable thread count
- **Flexible port specs** — ranges, lists, or mixed formats
- **Service identification** from common port mappings
- **Banner grabbing** on open ports
- **Formatted table output** and JSON export
- **Standalone binary** — no Python or pip required

## Example output

```bash
$ hawk target 127.0.0.1 --ports "80,3306"

Hawkeyes Scan Configuration:
  Target: 127.0.0.1
  Ports: 2 ports (80,3306)
  Threads: 100
  Timeout: 1.0s

Starting scan...
Port 80/tcp open     HAProxy-HTTP    [HTTP/1.1 200 OK...]
Port 3306/tcp open   MySQL           [8.4.8-0ubuntu0.25.10.1...]

====================================================================================================
SCAN RESULTS FOR 127.0.0.1
====================================================================================================
Target:        127.0.0.1 (127.0.0.1)
Scan time:     0.01 seconds
Ports scanned: 2
Open ports:    2
Success rate:  100.0%
====================================================================================================
Port     Status       Service              Banner
----------------------------------------------------------------------------------------------------
80       open         HAProxy-HTTP         HTTP/1.1 200 OK...
3306     open         MySQL                8.4.8-0ubuntu0.25.10.1...
====================================================================================================
```

## Security and ethics

- Designed for **educational cybersecurity** learning
- **Never scan targets** without explicit authorization
- Use reasonable thread counts and timeouts
- Follow all applicable laws and regulations

## License

MIT License — see [LICENSE](LICENSE) for details.
