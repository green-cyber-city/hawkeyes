#!/usr/bin/env python3

import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime


class ResultFormatter:
    """Utility class for formatting and displaying scan results."""
    
    def __init__(self, console_width: int = 100):
        """
        Initialize result formatter.
        
        Args:
            console_width: Maximum width for console output
        """
        self.console_width = console_width
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to specified length with ellipsis.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    def _print_separator(self, char: str = "=", length: Optional[int] = None):
        """Print a separator line."""
        sep_length = length or self.console_width
        print(char * sep_length)
    
    def _print_table_header(self):
        """Print table header for port results."""
        print(f"{'Port':<8} {'Status':<12} {'Service':<20} {'Banner'}")
        self._print_separator("-")
    
    def _format_port_row(self, port_result: Dict[str, Any]) -> str:
        """
        Format a single port result as a table row.
        
        Args:
            port_result: Dictionary with port result data
            
        Returns:
            Formatted table row string
        """
        port = port_result.get('port', 'N/A')
        status = port_result.get('status', 'unknown')
        service = port_result.get('service', 'Unknown')
        banner = port_result.get('banner', '')
        
        # Truncate banner for display
        banner_display = self._truncate_text(banner, 40)
        
        # Format row
        return f"{port:<8} {status:<12} {service:<20} {banner_display}"
    
    def print_scan_summary(self, results: Dict[str, Any]):
        """
        Print scan summary information.
        
        Args:
            results: Complete scan results dictionary
        """
        self._print_separator()
        print(f"SCAN RESULTS FOR {results.get('target', 'Unknown').upper()}")
        self._print_separator()
        
        # Summary information
        target = results.get('target', 'Unknown')
        resolved_ip = results.get('resolved_ip', 'Unknown')
        scan_time = results.get('scan_time', 0)
        total_ports = results.get('total_ports', 0)
        open_ports = results.get('open_ports', 0)
        
        print(f"Target:        {target} ({resolved_ip})")
        print(f"Scan time:     {scan_time:.2f} seconds")
        print(f"Ports scanned: {total_ports}")
        print(f"Open ports:    {open_ports}")
        
        if open_ports > 0:
            percentage = (open_ports / total_ports) * 100
            print(f"Success rate:  {percentage:.1f}%")
        
        self._print_separator()
    
    def print_results_table(self, results: Dict[str, Any], show_closed: bool = False):
        """
        Print scan results in a clean table format.
        
        Args:
            results: Complete scan results dictionary
            show_closed: Whether to show closed/filtered ports
        """
        port_results = results.get('results', [])
        
        if not port_results:
            print("No results to display.")
            return
        
        # Filter results based on show_closed flag
        if not show_closed:
            port_results = [r for r in port_results if r.get('status') == 'open']
        
        if not port_results:
            print("No open ports found.")
            return
        
        # Print table header
        self._print_table_header()
        
        # Print each result
        for port_result in port_results:
            print(self._format_port_row(port_result))
        
        # Add separator
        self._print_separator()
    
    def print_results_by_category(self, results: Dict[str, Any]):
        """
        Print results grouped by service category.
        
        Args:
            results: Complete scan results dictionary
        """
        try:
            from hawkeyes.utils.services import get_service_category
        except ImportError:
            try:
                from .services import get_service_category
            except ImportError:
                def get_service_category(port):
                    return "Other"
        
        port_results = results.get('results', [])
        open_ports = [r for r in port_results if r.get('status') == 'open']
        
        if not open_ports:
            print("No open ports found.")
            return
        
        # Group by category
        categories = {}
        for port_result in open_ports:
            port = port_result.get('port', 0)
            category = get_service_category(port)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(port_result)
        
        self._print_separator()
        print("RESULTS BY SERVICE CATEGORY")
        self._print_separator()
        
        # Print each category
        for category, ports in sorted(categories.items()):
            print(f"\n{category.upper()} ({len(ports)} ports):")
            print("-" * 40)
            
            for port_result in ports:
                banner = port_result.get('banner', '')
                banner_display = self._truncate_text(banner, 50)
                
                print(f"  Port {port_result.get('port'):<5} - {port_result.get('service', 'Unknown'):<15}")
                if banner_display:
                    print(f"         {banner_display}")
        
        self._print_separator()
    
    def print_detailed_results(self, results: Dict[str, Any]):
        """
        Print detailed results with full information.
        
        Args:
            results: Complete scan results dictionary
        """
        self.print_scan_summary(results)
        
        port_results = results.get('results', [])
        open_ports = [r for r in port_results if r.get('status') == 'open']
        
        if not open_ports:
            print("No open ports found.")
            return
        
        print(f"\nDETAILED PORT INFORMATION:")
        self._print_separator("-")
        
        for port_result in open_ports:
            port = port_result.get('port')
            service = port_result.get('service', 'Unknown')
            banner = port_result.get('banner', '')
            
            print(f"\nPort {port}/tcp - {service}")
            print("-" * 30)
            
            if banner:
                print(f"Banner: {banner}")
            else:
                print("Banner: No banner captured")
    
    def save_to_json(self, results: Dict[str, Any], filename: str, pretty: bool = True) -> bool:
        """
        Save scan results to JSON file.
        
        Args:
            results: Complete scan results dictionary
            filename: Output filename
            pretty: Whether to format JSON for readability
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from hawkeyes import __version__ as scanner_version
        except ImportError:
            scanner_version = '1.0.0'

        try:
            # Add metadata
            results_with_metadata = results.copy()
            results_with_metadata['scan_metadata'] = {
                'scanner_version': scanner_version,
                'timestamp': datetime.now().isoformat(),
                'format_version': '1.0'
            }
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(results_with_metadata, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(results_with_metadata, f, ensure_ascii=False)
            
            return True
            
        except (OSError, IOError) as e:
            print(f"Error writing to file {filename}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error saving to JSON: {e}")
            return False
    
    def print_and_save(self, results: Dict[str, Any], output_file: Optional[str] = None, 
                      format_type: str = 'table', show_closed: bool = False):
        """
        Print results and optionally save to file.
        
        Args:
            results: Complete scan results dictionary
            output_file: Optional JSON output filename
            format_type: Display format ('table', 'category', 'detailed')
            show_closed: Whether to show closed/filtered ports
        """
        # Print results
        if format_type == 'table':
            self.print_scan_summary(results)
            self.print_results_table(results, show_closed)
        elif format_type == 'category':
            self.print_scan_summary(results)
            self.print_results_by_category(results)
        elif format_type == 'detailed':
            self.print_detailed_results(results)
        else:
            print(f"Unknown format type: {format_type}")
            return
        
        # Save to file if requested
        if output_file:
            if self.save_to_json(results, output_file):
                print(f"\nResults saved to: {output_file}")
            else:
                print(f"\nFailed to save results to: {output_file}")


def format_results_simple(results: Dict[str, Any], output_file: Optional[str] = None):
    """
    Simple function to format and save results.
    
    Args:
        results: Complete scan results dictionary
        output_file: Optional JSON output filename
    """
    formatter = ResultFormatter()
    formatter.print_and_save(results, output_file)


def print_quick_summary(results: Dict[str, Any]):
    """
    Print a quick summary of scan results.
    
    Args:
        results: Complete scan results dictionary
    """
    target = results.get('target', 'Unknown')
    resolved_ip = results.get('resolved_ip', 'Unknown')
    scan_time = results.get('scan_time', 0)
    total_ports = results.get('total_ports', 0)
    open_ports = results.get('open_ports', 0)
    
    print(f"\nScan Summary:")
    print(f"  Target: {target} ({resolved_ip})")
    print(f"  Time: {scan_time:.2f}s")
    print(f"  Ports: {total_ports} scanned, {open_ports} open")
    
    if open_ports > 0:
        port_results = results.get('results', [])
        open_port_list = [r.get('port') for r in port_results if r.get('status') == 'open']
        print(f"  Open: {', '.join(map(str, sorted(open_port_list)))}")


# Test function
if __name__ == "__main__":
    # Sample test data
    test_results = {
        'target': 'example.com',
        'resolved_ip': '93.184.216.34',
        'scan_time': 2.15,
        'total_ports': 100,
        'open_ports': 3,
        'results': [
            {'port': 80, 'status': 'open', 'service': 'HTTP', 'banner': 'HTTP/1.1 200 OK\nServer: Apache'},
            {'port': 443, 'status': 'open', 'service': 'HTTPS', 'banner': 'HTTPS handshake'},
            {'port': 22, 'status': 'closed', 'service': 'SSH', 'banner': None},
            {'port': 3306, 'status': 'filtered', 'service': 'MySQL', 'banner': None}
        ]
    }
    
    formatter = ResultFormatter()
    
    print("=== Table Format ===")
    formatter.print_and_save(test_results, format_type='table')
    
    print("\n=== Category Format ===")
    formatter.print_and_save(test_results, format_type='category')
    
    print("\n=== Detailed Format ===")
    formatter.print_and_save(test_results, format_type='detailed')
    
    print("\n=== Quick Summary ===")
    print_quick_summary(test_results)
    
    # Test JSON saving
    json_saved = formatter.save_to_json(test_results, "test_results.json")
    if json_saved:
        print("\nJSON test output saved to test_results.json")