#!/usr/bin/env python3
"""
Enhanced Monitor Launcher
Easy launcher for the Khazad-dûm enhanced monitoring system
"""

import os
import sys
import subprocess
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Khazad-dûm Trading Monitor Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_enhanced.py                    # Run with live data
  python run_enhanced.py --mock             # Run with mock data
  python run_enhanced.py --demo             # Demo mode (mock + fast refresh)
  python run_enhanced.py --refresh 10      # Custom refresh interval
  
Controls (when running):
  r = force refresh data
  m = toggle between mock/live data mode
  q = quit
        """
    )
    
    parser.add_argument('--mock', action='store_true',
                       help='Use mock data instead of live database')
    parser.add_argument('--demo', action='store_true',
                       help='Demo mode: mock data with fast refresh (2s)')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds (default: 5)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose output')
    
    args = parser.parse_args()
    
    # Build command
    cmd = [sys.executable, 'khazad_monitor/enhanced_monitor.py']
    
    if args.demo:
        cmd.extend(['--mock', '--refresh', '2'])
        print("🚀 Starting Enhanced Monitor in DEMO mode...")
        print("   - Using mock data")
        print("   - Fast refresh (2 seconds)")
    elif args.mock:
        cmd.append('--mock')
        cmd.extend(['--refresh', str(args.refresh)])
        print("🧪 Starting Enhanced Monitor with MOCK data...")
    else:
        cmd.extend(['--refresh', str(args.refresh)])
        print("📈 Starting Enhanced Monitor with LIVE data...")
    
    print(f"   - Refresh interval: {args.refresh if not args.demo else 2} seconds")
    print(f"   - Press 'q' to quit, 'r' to refresh, 'm' to toggle data mode")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(project_root)
    
    try:
        # Run the monitor
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✋ Monitor stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running monitor: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()