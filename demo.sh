#!/bin/bash

# Quick Demo Script for TCP Port Scanner
# This script demonstrates various scanning scenarios

echo "🚀 TCP Port Scanner - Quick Demo"
echo "================================"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

# Function to print command
print_command() {
    echo -e "${GREEN}$ $1${NC}"
}

# Function to run demonstration
demo_scan() {
    local target=$1
    local ports=$2
    local description=$3
    
    print_section "$description"
    print_command "python3 main.py --target $target --ports \"$ports\""
    echo
    
    if command -v python3 &> /dev/null; then
        python3 main.py --target "$target" --ports "$ports" --output "demo_${target//[^a-zA-Z0-9]/_}_$(date +%s).json"
    else
        echo -e "${RED}Python 3 not found. Please install Python 3 to run the scanner.${NC}"
    fi
    
    echo
    echo "Press Enter to continue..."
    read -r
}

echo -e "${YELLOW}This demo script shows various ways to use the TCP Port Scanner.${NC}"
echo -e "${YELLOW}Follow along and learn the different scanning techniques.${NC}"
echo

# Demo 1: Basic Localhost Scan
demo_scan "127.0.0.1" "80,443,3306,22,25" "1️⃣ Basic Localhost Scan - Common Services"

# Demo 2: Port Range
demo_scan "127.0.0.1" "1-100" "2️⃣ Port Range Scan - First 100 Ports"

# Demo 3: Website Scan
demo_scan "example.com" "80,443,8080,8443" "3️⃣ Web Server Scan - Multiple Web Ports"

# Demo 4: High Thread Count
print_section "4️⃣ High-Speed Scan - Using More Threads"
print_command "python3 main.py --target example.com --ports \"1-1000\" --threads 200"
echo

if command -v python3 &> /dev/null; then
    python3 main.py --target example.com --ports "1-1000" --threads 200 --timeout 0.5
else
    echo -e "${RED}Python 3 not found. Please install Python 3 to run the scanner.${NC}"
fi

echo
echo "Press Enter to continue..."
read -r

# Demo 5: Save to JSON
demo_scan "example.com" "80,443" "5️⃣ Save Results to JSON File"

# Demo 6: Service-Specific Scans
print_section "6️⃣ Service-Specific Scans"

echo "Database Services:"
print_command "python3 main.py --target 127.0.0.1 --ports \"3306,5432,1433,1521,27017,6379\""
echo

echo "Remote Access Services:"
print_command "python3 main.py --target 127.0.0.1 --ports \"22,23,3389,5900,5901\""
echo

echo "Email Services:"
print_command "python3 main.py --target example.com --ports \"25,587,110,143,993,995\""
echo

echo "Press Enter to continue..."
read -r

# Demo 7: Error Handling Examples
print_section "7️⃣ Error Handling Examples"

echo "Invalid Target:"
print_command "python3 main.py --target invalid-domain-that-does-not-exist.com --ports 80"
echo

echo "Invalid Port Specification:"
print_command "python3 main.py --target 127.0.0.1 --ports \"invalid,ports,here\""
echo

echo "Press Enter to continue..."
read -r

# Final section
print_section "🎉 Demo Complete!"
echo
echo "You've seen various scanning scenarios:"
echo "✅ Basic localhost scanning"
echo "✅ Port range scanning"  
echo "✅ Website scanning"
echo "✅ High-speed scanning"
echo "✅ JSON output"
echo "✅ Service-specific scanning"
echo "✅ Error handling"
echo
echo -e "${YELLOW}📚 Next Steps:${NC}"
echo "1. Read the USER_GUIDE.md for comprehensive documentation"
echo "2. Check README.md for project overview"
echo "3. Examine the source code to learn how it works"
echo "4. Try scanning your own authorized targets"
echo
echo -e "${BLUE}⚠️  Remember:${NC} Only scan targets you own or have permission to scan!"
echo
echo -e "${GREEN}Happy learning and stay safe! 🚀${NC}"