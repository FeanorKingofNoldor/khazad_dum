#!/usr/bin/env python3
"""
Diagnose the exact TradingAgents import issues
"""

import sys
from pathlib import Path
import ast

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def check_file_imports(file_path):
    """Check imports in a specific file"""
    
    if not file_path.exists():
        return f"File not found: {file_path}"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all import lines
    import_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'tradingagents' in line.lower() and not line.strip().startswith('#'):
            import_lines.append((i, line.strip()))
    
    return import_lines

def main():
    print("\n" + "="*60)
    print("TRADINGAGENTS IMPORT DIAGNOSTIC")
    print("="*60)
    
    # Check key files
    files_to_check = [
        "src/trading_engines/tradingagents_integration/batch_processor.py",
        "src/trading_engines/tradingagents_integration/agent_coordinator.py", 
        "src/trading_engines/tradingagents_integration/agent_wrapper.py",
        "main.py",
    ]
    
    print("\n1. Checking import statements in key files:")
    
    for file_path in files_to_check:
        path = Path(file_path)
        print(f"\n  {file_path}:")
        
        result = check_file_imports(path)
        
        if isinstance(result, str):
            print(f"    {result}")
        elif result:
            for line_num, line in result:
                print(f"    Line {line_num}: {line}")
        else:
            print("    No tradingagents imports found")
    
    print("\n2. Checking tradingagents_lib structure:")
    
    lib_path = Path("tradingagents_lib")
    
    if not lib_path.exists():
        print("  ✗ tradingagents_lib NOT FOUND at project root")
        print("\n  This is the problem! The library is missing.")
        print("\n  Solutions:")
        print("  1. Check if it's in a different location")
        print("  2. Clone/copy it to the project root")
        print("  3. Install it as a package")
    else:
        print(f"  ✓ tradingagents_lib exists at {lib_path.resolve()}")
        
        # Check structure
        expected_paths = [
            "tradingagents_lib/tradingagents",
            "tradingagents_lib/tradingagents/__init__.py",
            "tradingagents_lib/tradingagents/agents",
            "tradingagents_lib/tradingagents/agents/__init__.py",
        ]
        
        for expected in expected_paths:
            path = Path(expected)
            if path.exists():
                print(f"    ✓ {expected}")
            else:
                print(f"    ✗ {expected} MISSING")
    
    print("\n3. Testing import directly:")
    
    test_imports = [
        ("tradingagents.agents", "from tradingagents.agents import *"),
        ("tradingagents_lib.tradingagents.agents", "from tradingagents_lib.tradingagents.agents import *"),
    ]
    
    for name, import_stmt in test_imports:
        print(f"\n  Testing: {import_stmt}")
        try:
            exec(import_stmt)
            print(f"    ✓ {name} imports successfully")
        except ImportError as e:
            print(f"    ✗ {name} failed: {e}")
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()