#!/bin/bash

echo "=== TCP Port Scanner Usage Examples ==="
echo

echo "1. Basic scan of common ports on localhost:"
echo "python3 port_scanner.py 127.0.0.1 -p 1-1000"
echo

echo "2. Scan specific ports on a website:"
echo "python3 port_scanner.py example.com -p 80,443,8080"
echo

echo "3. Fast scan with more threads:"
echo "python3 port_scanner.py 192.168.1.1 -p 1-65535 -T 200"
echo

echo "4. Scan with custom timeout:"
echo "python3 port_scanner.py google.com -p 80,443 -t 0.5"
echo

echo "5. Save results to JSON file:"
echo "python3 port_scanner.py localhost -p 1-1000 -o scan_results.json"
echo

echo "6. Scan without banner grabbing (faster):"
echo "python3 port_scanner.py 127.0.0.1 -p 1-1000 --no-banner"
echo

echo "7. Scan a port range:"
echo "python3 port_scanner.py 127.0.0.1 -p 8000-9000"
echo

echo "8. Complex port specification:"
echo "python3 port_scanner.py example.com -p 22,80,443,8080,9000-9100"
echo

read -p "Press Enter to run a basic scan of localhost ports 1-1000..."
python3 port_scanner.py 127.0.0.1 -p 1-1000