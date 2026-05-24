# Hawkeyes

A multithreaded TCP port scanner for educational cybersecurity. Hawkeyes scans TCP ports, identifies services, and grabs banners.

> **Authorized use only.** Only scan systems you own or have explicit permission to test.

## Install (Linux)

No Python. No pip. One command:

```bash
curl -fsSL https://YOUR-INSTALL-HOST/install.sh | sh
```

Replace `YOUR-INSTALL-HOST` with the URL where you host `install.sh` (see [PUBLISHING.md](PUBLISHING.md) for setup).

After install:

```bash
hawk
hawk target example.com --ports "80,443"
```

The installer downloads a standalone binary to `~/.local/bin/hawk`. If that directory is not in your PATH, the installer tells you what to add.

## Usage

Show the Hawkeyes banner:

```bash
hawk
```

Scan a target:

```bash
hawk target example.com --ports "80,443"
hawk target 127.0.0.1 --ports "1-1000"
hawk target 192.168.1.1 --ports "22,80,443" --threads 200 --timeout 2.0
hawk target example.com --ports "80,443" --output scan_results.json
```

### Options

```
hawk                          Show banner and usage info
hawk target HOST [options]    Scan TCP ports on a target

  --ports PORTS     Ports to scan (default: "1-1000")
  --threads N       Concurrent threads (default: 100, max: 1000)
  --timeout SECS    Connection timeout (default: 1.0, max: 30)
  --output FILE     Save results as JSON
```

## Features

- Multithreaded scanning
- Flexible port specs — ranges, lists, or mixed
- Service identification and banner grabbing
- Table output and JSON export
- Standalone install — no Python or pip required

## Security and ethics

- Designed for educational cybersecurity learning
- Never scan targets without authorization

## License

MIT License.
