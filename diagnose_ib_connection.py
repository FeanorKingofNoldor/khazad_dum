#!/usr/bin/env python3
"""
Comprehensive IB Connection Diagnostic Tool
Tests various connection methods to identify the exact issue
"""

import socket
import time
import sys
import os
import subprocess
from pathlib import Path

def check_port(port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def check_ib_processes():
    """Check for running IB processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = []
        for line in result.stdout.split('\n'):
            if any(term in line.lower() for term in ['ibgateway', 'tws', 'trader']) and 'grep' not in line:
                processes.append(line[:80])  # First 80 chars
        return processes
    except:
        return []

def check_config_files():
    """Check for IB configuration files"""
    config_locations = [
        Path.home() / 'Jts' / 'jts.ini',
        Path.home() / 'ibgateway',
        Path.home() / 'tws',
    ]
    
    found = []
    for loc in config_locations:
        if loc.exists():
            found.append(str(loc))
    return found

def test_raw_socket():
    """Test raw socket connection"""
    if not check_port(4002):
        return False, "Port 4002 not open"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(('127.0.0.1', 4002))
        
        # Try sending a simple test message
        sock.send(b'test\n')
        sock.settimeout(1)
        
        try:
            response = sock.recv(100)
            sock.close()
            return True, f"Got response: {response[:50]}"
        except socket.timeout:
            sock.close()
            return False, "No response from API (timeout)"
    except Exception as e:
        return False, f"Socket error: {e}"

def test_ib_async_import():
    """Test if ib_async can be imported"""
    try:
        import ib_async
        return True, f"ib_async version {ib_async.__version__}"
    except ImportError as e:
        return False, f"Cannot import ib_async: {e}"

def check_network_interfaces():
    """Check network interfaces"""
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    interfaces.append(parts[1])
        return interfaces
    except:
        return ["Unable to check"]

def main():
    print("=" * 60)
    print("IB CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # 1. Check processes
    print("\n1. CHECKING IB PROCESSES:")
    processes = check_ib_processes()
    if processes:
        print("   ⚠️  Found IB processes:")
        for p in processes:
            print(f"      {p}")
    else:
        print("   ✅ No IB processes running (clean state)")
    
    # 2. Check ports
    print("\n2. CHECKING PORTS:")
    for port in [4001, 4002]:
        if check_port(port):
            print(f"   ⚠️  Port {port} is OPEN")
        else:
            print(f"   ✅ Port {port} is closed")
    
    # 3. Check config files
    print("\n3. CHECKING CONFIG FILES:")
    configs = check_config_files()
    if configs:
        print("   Found configurations:")
        for c in configs:
            print(f"      {c}")
    else:
        print("   No IB configurations found")
    
    # 4. Check network
    print("\n4. CHECKING NETWORK:")
    interfaces = check_network_interfaces()
    print("   Network interfaces:")
    for iface in interfaces:
        print(f"      {iface}")
    
    # 5. Check ib_async
    print("\n5. CHECKING IB_ASYNC:")
    success, msg = test_ib_async_import()
    if success:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ {msg}")
    
    # 6. Test socket if port is open
    if check_port(4002):
        print("\n6. TESTING RAW SOCKET:")
        success, msg = test_raw_socket()
        if success:
            print(f"   ✅ {msg}")
        else:
            print(f"   ❌ {msg}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    
    if not check_port(4002):
        print("• Start TWS or IB Gateway first")
        print("• Make sure to log into Paper Trading mode")
    elif processes:
        print("• Multiple IB processes may cause conflicts")
        print("• Kill all processes and restart just one")
    else:
        print("• Port is open but API not responding")
        print("• Check API settings in TWS/Gateway")
        print("• Look for connection approval dialogs")
        print("• Try restarting with fresh config")
    
    print("=" * 60)

if __name__ == "__main__":
    main()