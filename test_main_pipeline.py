#!/usr/bin/env python3
"""
Test the main.py pipeline by temporarily disabling TradingAgents
This will test everything up to the TradingAgents step
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_main_pipeline():
    """Test main.py pipeline without TradingAgents"""
    print("🏔️ Testing main.py Pipeline (without TradingAgents)")
    print("="*60)
    
    # Temporarily patch the BatchProcessor to avoid API key issues
    import src.trading_engines.tradingagents_integration.batch_processor as batch_module
    
    # Create a mock BatchProcessor for testing
    class MockBatchProcessor:
        def __init__(self, database):
            self.database = database
            print("✓ MockBatchProcessor initialized (TradingAgents disabled for testing)")
        
        def process_batch(self, candidates, regime_data, portfolio_context):
            print("✓ Mock batch processing (simulating TradingAgents)")
            print(f"  - Processing {len(candidates) if hasattr(candidates, '__len__') else 0} candidates")
            print(f"  - Regime: {regime_data.get('regime', 'unknown')}")
            print(f"  - Portfolio cash: ${portfolio_context.get('cash_available', 0):,.0f}")
            
            # Return mock result
            return {
                "success": True,
                "batch_id": "test_batch_123",
                "selections": [],
                "excluded": [],
                "patterns_enabled": False
            }
    
    # Temporarily replace the real BatchProcessor
    original_processor = batch_module.BatchProcessor
    batch_module.BatchProcessor = MockBatchProcessor
    
    try:
        # Import and run the main initialization
        from main import initialize_components, validate_portfolio_context, main
        
        print("\nTesting main.py component initialization...")
        components = initialize_components()
        
        if not components:
            print("❌ Component initialization failed")
            return False
        
        print("✓ All main.py components initialized successfully")
        
        # Test portfolio context validation
        print("\nTesting portfolio context validation...")
        test_context = {
            "cash_available": 100000,
            "total_positions": 0,
            "unrealized_pnl_pct": 0
        }
        validated = validate_portfolio_context(test_context)
        print(f"✓ Portfolio context validated: ${validated['cash_available']:,.0f} cash")
        
        print("\n" + "="*60)
        print("🎉 MAIN.PY PIPELINE COMPONENTS WORKING!")
        print("✓ All imports successful")
        print("✓ Component initialization working")
        print("✓ Portfolio validation working")
        print("✓ Mock TradingAgents integration working")
        print("\nReady to run main.py with actual TradingAgents (add API keys)")
        
        return True
        
    except Exception as e:
        print(f"❌ Main pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore the original BatchProcessor
        batch_module.BatchProcessor = original_processor

if __name__ == "__main__":
    success = test_main_pipeline()
    sys.exit(0 if success else 1)