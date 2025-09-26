#!/usr/bin/env python3
"""
Fix the remaining TradingAgents import issues
"""

from pathlib import Path
import re

def fix_all_tradingagents_imports():
    """Find and fix all imports of tradingagents"""
    
    print("\nSearching for files with tradingagents imports...")
    
    # Search patterns to fix
    patterns_to_fix = [
        (r"from tradingagents\.agents", "from tradingagents_lib.tradingagents.agents"),
        (r"from tradingagents\.", "from tradingagents_lib.tradingagents."),
        (r"import tradingagents\b", "import tradingagents_lib.tradingagents as tradingagents"),
        (r"from tradingagents import", "from tradingagents_lib.tradingagents import"),
    ]
    
    # Files to check
    files_to_check = [
        "src/trading_engines/tradingagents_integration/batch_processor.py",
        "src/trading_engines/tradingagents_integration/agent_coordinator.py",
        "src/trading_engines/tradingagents_integration/agent_wrapper.py",
        "src/trading_engines/tradingagents_integration/portfolio_context.py",
        "src/compat.py",
        "main.py",
        "src/batch/overnight_processor.py",  # In case this exists
        "src/tradingagents/analyzer.py",  # In case these exist
        "src/tradingagents/client.py",
        "src/tradingagents/context_provider.py",
    ]
    
    # Also search for any other Python files that might have tradingagents imports
    all_py_files = list(Path("src").rglob("*.py"))
    all_py_files.append(Path("main.py"))
    
    fixed_files = []
    
    for file_path in all_py_files:
        if "__pycache__" in str(file_path) or not file_path.exists():
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                original_content = content
            
            # Check if file has tradingagents imports
            if "tradingagents" in content and "tradingagents_lib" not in content:
                print(f"\n  Checking: {file_path}")
                
                # Apply all fixes
                for pattern, replacement in patterns_to_fix:
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        print(f"    Fixed: {pattern} -> {replacement}")
                
                # Save if changed
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    fixed_files.append(file_path)
                    print(f"    ✓ Saved fixes to {file_path}")
                    
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    
    return fixed_files


def verify_tradingagents_lib_structure():
    """Verify the tradingagents_lib structure"""
    
    print("\nVerifying tradingagents_lib structure...")
    
    required_paths = [
        "tradingagents_lib",
        "tradingagents_lib/tradingagents",
        "tradingagents_lib/tradingagents/agents",
        "tradingagents_lib/tradingagents/graph",
    ]
    
    all_exist = True
    for path_str in required_paths:
        path = Path(path_str)
        if path.exists():
            print(f"  ✓ {path_str} exists")
        else:
            print(f"  ✗ {path_str} MISSING")
            all_exist = False
    
    # Check for __init__.py files
    if all_exist:
        init_files = [
            "tradingagents_lib/tradingagents/__init__.py",
            "tradingagents_lib/tradingagents/agents/__init__.py",
        ]
        
        for init_path_str in init_files:
            init_path = Path(init_path_str)
            if init_path.exists():
                print(f"  ✓ {init_path_str} exists")
            else:
                print(f"  ⚠ {init_path_str} missing (creating...)")
                init_path.touch()
    
    return all_exist


def create_test_import_script():
    """Create a simple test script to verify the fix"""
    
    test_script = Path("test_tradingagents_import.py")
    
    content = '''#!/usr/bin/env python3
"""Test TradingAgents imports specifically"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing TradingAgents imports...")

try:
    from tradingagents_lib.tradingagents.agents import BaseAgent
    print("✓ Direct import from tradingagents_lib works")
except ImportError as e:
    print(f"✗ Direct import failed: {e}")

try:
    from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
    print("✓ BatchProcessor imports successfully")
except ImportError as e:
    print(f"✗ BatchProcessor import failed: {e}")

try:
    import main
    print("✓ main.py imports successfully")
except ImportError as e:
    print(f"✗ main.py import failed: {e}")

print("\\nTest complete!")
'''
    
    with open(test_script, 'w') as f:
        f.write(content)
    
    print(f"\nCreated test script: {test_script}")


def main():
    print("\n" + "="*60)
    print("FIXING TRADINGAGENTS IMPORT ISSUES")
    print("="*60)
    
    # First verify the library structure
    lib_exists = verify_tradingagents_lib_structure()
    
    if not lib_exists:
        print("\n⚠ WARNING: tradingagents_lib structure is incomplete!")
        print("Make sure tradingagents_lib is properly installed at the project root")
        print("\nExpected structure:")
        print("  tradingagents_lib/")
        print("    tradingagents/")
        print("      agents/")
        print("      graph/")
        print("      ...")
        return
    
    # Fix all imports
    fixed_files = fix_all_tradingagents_imports()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if fixed_files:
        print(f"\n✓ Fixed {len(fixed_files)} files:")
        for file in fixed_files[:10]:  # Show first 10
            print(f"  • {file}")
        if len(fixed_files) > 10:
            print(f"  ... and {len(fixed_files) - 10} more")
    else:
        print("\n⚠ No files needed fixing (or all already fixed)")
    
    # Create test script
    create_test_import_script()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
    print("\n1. Test the specific import:")
    print("   python test_tradingagents_import.py")
    
    print("\n2. Test all imports again:")
    print("   python scripts/test_khazad_dum_imports_fixed.py")
    
    print("\n3. If still failing, check the actual import in batch_processor.py:")
    print("   grep -n 'import tradingagents' src/trading_engines/tradingagents_integration/batch_processor.py")


if __name__ == "__main__":
    main()