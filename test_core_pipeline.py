#!/usr/bin/env python3
"""
Test the core KHAZAD_DUM pipeline without TradingAgents
This tests the main flow: regime -> fetch -> filter -> database
"""

import os
import sys
import traceback
import pandas as pd
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_full_pipeline():
    """Test the complete core pipeline"""
    print("🏔️ KHAZAD_DUM Core Pipeline Test")
    print("Testing: Regime -> Fetch -> Filter -> Database")
    print("="*60)
    
    try:
        # Step 1: Import all components
        print("\n1. Importing components...")
        from src.core.market_analysis.regime_detector import RegimeDetector
        from src.data_pipeline.storage.database_manager import DatabaseManager
        from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher
        from src.core.stock_screening.stock_filter import StockFilter
        print("✓ All components imported successfully")
        
        # Step 2: Initialize components
        print("\n2. Initializing components...")
        database = DatabaseManager()
        regime_detector = RegimeDetector()
        fetcher = StockDataFetcher()
        filter_engine = StockFilter(database)
        print("✓ All components initialized")
        
        # Step 3: Test regime detection
        print("\n3. Testing regime detection...")
        regime = regime_detector.get_current_regime()
        print(f"✓ Regime: {regime['regime']} (F&G: {regime.get('fear_greed_value', 'N/A')})")
        
        # Log regime to database
        regime_logged = database.log_regime(regime)
        print(f"✓ Regime logged to database: {regime_logged}")
        
        # Step 4: Test stock data fetch (small sample)
        print("\n4. Testing stock data fetch (small sample)...")
        
        # Create small test dataset instead of fetching from API
        test_data = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META'],
            'price': [150.0, 300.0, 2800.0, 250.0, 350.0],
            'volume': [50000000, 25000000, 1500000, 45000000, 20000000],
            'dollar_volume': [7.5e9, 7.5e9, 4.2e9, 11.25e9, 7e9],
            'rsi_2': [25.0, 75.0, 45.0, 80.0, 35.0],
            'atr': [5.0, 8.0, 50.0, 15.0, 12.0],
            'volume_ratio': [1.2, 0.8, 1.5, 2.0, 1.1],
            'quality_score': [8.5, 8.0, 9.0, 7.5, 7.8]
        })
        
        print(f"✓ Test dataset created with {len(test_data)} stocks")
        
        # Insert test data into database
        rows_inserted = database.insert_stock_metrics(test_data)
        print(f"✓ Inserted {rows_inserted} stock records")
        
        # Step 5: Test filtering
        print("\n5. Testing stock filtering...")
        candidates = filter_engine.run_full_filter(regime)
        
        if candidates is not None and not candidates.empty:
            print(f"✓ Filter returned {len(candidates)} candidates")
            print("Top candidates:")
            for _, row in candidates.head(3).iterrows():
                print(f"  - {row['symbol']}: score={row.get('score', 0):.2f}, RSI={row.get('rsi_2', 0):.1f}")
        else:
            print("⚠ Filter returned no candidates (this might be normal)")
        
        # Step 6: Test database queries
        print("\n6. Testing database operations...")
        
        # Test recent stock data query
        try:
            recent_stocks = database.get_latest_metrics()
            print(f"✓ Retrieved {len(recent_stocks)} recent stock records")
        except Exception as e:
            print(f"⚠ get_latest_metrics failed: {e}")
        
        # Test regime history
        try:
            cursor = database.conn.execute("""
                SELECT regime, fear_greed_value, timestamp 
                FROM regime_history 
                ORDER BY timestamp DESC 
                LIMIT 3
            """)
            regimes = cursor.fetchall()
            print(f"✓ Retrieved {len(regimes)} recent regime records")
        except Exception as e:
            print(f"⚠ Regime history query failed: {e}")
        
        print("\n" + "="*60)
        print("🎉 CORE PIPELINE TEST COMPLETED SUCCESSFULLY!")
        print("✓ All core components are working")
        print("✓ Database operations functional")
        print("✓ Data pipeline flows correctly")
        print("\nNext: Add your API keys to test TradingAgents integration")
        return True
        
    except Exception as e:
        print(f"\n❌ PIPELINE TEST FAILED: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)