#!/usr/bin/env python3
"""
Diagnostic script to identify Python import issues
"""

import os
import sys
from pathlib import Path

def diagnose():
    print("\n" + "="*60)
    print("KHAZAD_DUM IMPORT DIAGNOSTIC")
    print("="*60)
    
    # 1. Check current working directory
    print("\n1. Current Working Directory:")
    cwd = Path.cwd()
    print(f"   {cwd}")
    
    # 2. Check Python path
    print("\n2. Python Path:")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"   [{i}] {path}")
    
    # 3. Check if src exists
    print("\n3. Checking src directory:")
    src_path = cwd / "src"
    if src_path.exists():
        print(f"   ✓ src/ exists at {src_path}")
        
        # Check for __init__.py
        src_init = src_path / "__init__.py"
        if src_init.exists():
            print(f"   ✓ src/__init__.py exists")
        else:
            print(f"   ❌ src/__init__.py MISSING - This is the problem!")
    else:
        print(f"   ❌ src/ directory not found at {src_path}")
        print("   Looking for src in parent directories...")
        
        # Look up the tree
        parent = cwd.parent
        while parent != parent.parent:
            possible_src = parent / "src"
            if possible_src.exists():
                print(f"   ✓ Found src/ at {possible_src}")
                print(f"   → You should run scripts from: {parent}")
                break
            parent = parent.parent
    
    # 4. Check key subdirectories
    print("\n4. Checking key subdirectories:")
    key_dirs = [
        "src/core",
        "src/core/market_analysis",
        "src/data_pipeline",
        "src/trading_engines"
    ]
    
    for dir_path in key_dirs:
        full_path = cwd / dir_path
        if full_path.exists():
            init_file = full_path / "__init__.py"
            if init_file.exists():
                print(f"   ✓ {dir_path}/__init__.py exists")
            else:
                print(f"   ⚠ {dir_path}/ exists but __init__.py MISSING")
        else:
            print(f"   ✗ {dir_path}/ not found")
    
    # 5. Try a simple import with path manipulation
    print("\n5. Testing import with path fix:")
    
    # Add current directory to path
    if str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))
        print(f"   Added {cwd} to Python path")
    
    try:
        import src
        print("   ✓ 'import src' works!")
        
        # Try deeper import
        from src.core.market_analysis.regime_detector import RegimeDetector
        print("   ✓ Can import RegimeDetector!")
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        
        # Provide specific fix
        print("\n   FIX NEEDED:")
        if "No module named 'src'" in str(e):
            print("   1. Create src/__init__.py:")
            print("      echo '\"\"\"KHAZAD_DUM src package\"\"\"' > src/__init__.py")
            print("   2. Run from project root:")
            print(f"      cd {cwd}")
            print("      python your_script.py")
    
    # 6. List all __init__.py files
    print("\n6. Existing __init__.py files:")
    init_files = list(Path(".").rglob("__init__.py"))
    
    if init_files:
        for f in init_files[:10]:  # Show first 10
            print(f"   • {f}")
        if len(init_files) > 10:
            print(f"   ... and {len(init_files) - 10} more")
    else:
        print("   ❌ NO __init__.py files found!")
        print("   This is definitely the problem!")
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    diagnose()