#!/usr/bin/env python3
"""
IB Connection Fix - Alternative approach to connect to IB
Uses synchronous connection with proper event loop handling
"""

import sys
import time
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_connection_with_fix():
    """Test IB connection with fixes for common issues"""
    
    print("=" * 60)
    print("IB CONNECTION FIX TEST")
    print("=" * 60)
    
    # Import ib_async with proper setup
    try:
        from ib_async import IB, util
        print("✅ ib_async imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ib_async: {e}")
        return False
    
    # CRITICAL: Start the event loop first
    # This is often missing and causes timeouts
    print("\n1. Starting event loop...")
    util.startLoop()
    print("✅ Event loop started")
    
    # Create IB instance
    ib = IB()
    
    # Enable logging to see what's happening
    print("\n2. Enabling debug logging...")
    util.logToConsole(logging.WARNING)
    
    # Try different client IDs
    client_ids_to_try = [1, 2, 3, 99, 100]
    
    for client_id in client_ids_to_try:
        print(f"\n3. Attempting connection with Client ID {client_id}...")
        
        try:
            # Use synchronous connect with longer timeout
            ib.connect('127.0.0.1', 4002, clientId=client_id, timeout=20)
            
            if ib.isConnected():
                print(f"✅ CONNECTED with Client ID {client_id}!")
                
                # Wait for initial data
                print("\n4. Waiting for data sync...")
                time.sleep(3)
                
                # Test basic functionality
                print("\n5. Testing account data retrieval...")
                
                # Get account summary
                summary = ib.accountSummary()
                if summary:
                    print(f"   ✅ Account summary: {len(summary)} items")
                    for item in summary[:3]:
                        print(f"      {item.tag}: {item.value}")
                else:
                    print("   ⚠️  No account summary data")
                
                # Get positions
                positions = ib.positions()
                print(f"   ✅ Positions: {len(positions)} found")
                
                # Get portfolio
                portfolio = ib.portfolio()
                print(f"   ✅ Portfolio: {len(portfolio)} items")
                
                print("\n" + "=" * 60)
                print("✅ SUCCESS! Connection working!")
                print(f"Use Client ID {client_id} in your configuration")
                print("=" * 60)
                
                # Save working config
                config_file = Path.home() / 'khazad_dum' / '.ib_working_config'
                with open(config_file, 'w') as f:
                    f.write(f"CLIENT_ID={client_id}\n")
                    f.write("PORT=4002\n")
                    f.write("HOST=127.0.0.1\n")
                print(f"\n✅ Saved working config to {config_file}")
                
                # Disconnect cleanly
                ib.disconnect()
                return True
                
        except Exception as e:
            print(f"   ❌ Client ID {client_id} failed: {type(e).__name__}: {str(e)[:50]}")
            
            # Try to disconnect if connected
            try:
                if ib.isConnected():
                    ib.disconnect()
            except:
                pass
            
            # Small delay before trying next ID
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("❌ ALL CONNECTION ATTEMPTS FAILED")
    print("\nPossible causes:")
    print("1. TWS/IB Gateway not running")
    print("2. Not logged into Paper Trading")
    print("3. API not enabled in settings")
    print("4. Firewall blocking connection")
    print("5. Another client using all available IDs")
    print("=" * 60)
    
    return False

def check_prerequisites():
    """Check if TWS/Gateway is running"""
    import socket
    
    print("\nChecking prerequisites...")
    
    # Check if port is open
    sock = socket.socket()
    result = sock.connect_ex(('127.0.0.1', 4002))
    sock.close()
    
    if result != 0:
        print("❌ Port 4002 is not open")
        print("\nTo fix:")
        print("1. Start TWS with: /home/feanor/tws/tws")
        print("2. Login to Paper Trading account")
        print("3. Enable API in File → Global Configuration → API → Settings")
        print("4. Check 'Enable ActiveX and Socket Clients'")
        print("5. Set Socket port to 4002")
        return False
    else:
        print("✅ Port 4002 is open")
        return True

if __name__ == "__main__":
    if check_prerequisites():
        success = test_connection_with_fix()
        sys.exit(0 if success else 1)
    else:
        print("\n❌ Prerequisites not met. Please start TWS first.")
        sys.exit(1)