#!/usr/bin/env python3
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

print("\nTest complete!")
