"""
Data fetcher for KHAZAD_DUM monitoring
Real-time integration with the production database
"""

import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.data_pipeline.storage.database_manager import DatabaseManager
    from src.core.market_analysis.regime_detector import RegimeDetector
    from config.settings.base_config import DATABASE_PATH
except ImportError as e:
    print(f"Warning: Could not import production modules: {e}")
    print("Falling back to direct database access...")
    DATABASE_PATH = project_root / "config" / "data" / "databases" / "khazad_dum.db"


class DataFetcher:
    """Real-time data fetcher for Khazad-dûm monitoring system"""
    
    def __init__(self, use_mock: bool = False):
        self.db_manager = None
        self.regime_detector = None
        self.connection = None
        self.use_mock = use_mock
        
        if self.use_mock:
            print("✓ Using mock data mode")
            return
        
        # Try production database manager first
        try:
            self.db_manager = DatabaseManager()
            self.regime_detector = RegimeDetector()
            print("✓ Connected to production database")
        except Exception as e:
            print(f"Production database unavailable: {e}")
            # Try direct SQLite connection
            try:
                self.connect_direct_db()
                print("✓ Connected to SQLite database directly")
            except Exception as e2:
                print(f"Direct database connection failed: {e2}")
                print("⚠ Using mock data for demonstration")
                self.use_mock = True
    
    def init_db_connection(self) -> bool:
        """Initialize database connection for enhanced monitor"""
        if self.use_mock:
            return True
        
        # Try production database manager first
        try:
            self.db_manager = DatabaseManager()
            self.regime_detector = RegimeDetector()
            print("✓ Connected to production database")
            return True
        except Exception as e:
            print(f"Production database unavailable: {e}")
            # Try direct SQLite connection
            try:
                self.connect_direct_db()
                print("✓ Connected to SQLite database directly")
                return True
            except Exception as e2:
                print(f"Direct database connection failed: {e2}")
                self.use_mock = True
                return False
    
    def connect_direct_db(self):
        """Connect directly to SQLite database"""
        db_path = DATABASE_PATH
        if not db_path.exists():
            # Try to create the database directory
            db_path.parent.mkdir(parents=True, exist_ok=True)
            raise FileNotFoundError(f"Database not found at {db_path}")
        
        self.connection = sqlite3.connect(str(db_path))
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        if self.db_manager:
            try:
                self.db_manager.conn.close()
            except:
                pass
    
    def get_portfolio_positions(self) -> List[Dict]:
        """Get all current positions from the database"""
        if self.use_mock:
            return self._mock_positions()
        
        try:
            if self.db_manager:
                # Use production database manager
                cursor = self.db_manager.conn.execute("""
                    SELECT 
                        symbol,
                        quantity as shares,
                        entry_price,
                        entry_price as current_price,
                        stop_loss,
                        target_price,
                        pnl_dollars as unrealized_pnl,
                        pnl_pct as pnl_percentage,
                        entry_date,
                        status,
                        conviction_score
                    FROM position_tracking 
                    WHERE status = 'OPEN'
                    ORDER BY symbol
                """)
            else:
                # Use direct SQLite connection
                cursor = self.connection.execute("""
                    SELECT 
                        symbol,
                        quantity as shares,
                        entry_price,
                        entry_price as current_price,
                        stop_loss,
                        target_price,
                        pnl_dollars as unrealized_pnl,
                        pnl_pct as pnl_percentage,
                        entry_date,
                        status,
                        conviction_score
                    FROM position_tracking 
                    WHERE status = 'OPEN'
                    ORDER BY symbol
                """)
            
            positions = [dict(row) for row in cursor.fetchall()]
            
            # If no positions found, return mock data for demonstration
            if not positions:
                print("No active positions found in database, showing mock data")
                return self._mock_positions()
            
            return positions
            
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return self._mock_positions()
    
    def get_portfolio_value_history(self, days: int = 30) -> Tuple[List, List]:
        """Get portfolio value history from trading data"""
        if self.use_mock:
            return self._mock_portfolio_history(days)
        
        try:
            # Get historical performance data
            if self.db_manager:
                cursor = self.db_manager.conn.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        SUM(pnl_dollars) as daily_pnl
                    FROM position_tracking 
                    WHERE created_at >= date('now', '-{} days')
                    AND pnl_dollars IS NOT NULL
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """.format(days))
            else:
                cursor = self.connection.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        SUM(pnl_dollars) as daily_pnl
                    FROM position_tracking 
                    WHERE created_at >= date('now', '-{} days')
                    AND pnl_dollars IS NOT NULL
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """.format(days))
            
            results = cursor.fetchall()
            
            if not results:
                return self._mock_portfolio_history(days)
            
            dates = [datetime.strptime(r[0], '%Y-%m-%d') if isinstance(r[0], str) else r[0] for r in results]
            # Calculate cumulative portfolio value
            base_value = 100000  # Starting portfolio value
            values = []
            cumulative_pnl = 0
            
            for r in results:
                cumulative_pnl += r[1] if r[1] else 0
                values.append(base_value + cumulative_pnl)
            
            return dates, values
            
        except Exception as e:
            print(f"Error fetching portfolio history: {e}")
            return self._mock_portfolio_history(days)
    
    def get_position_history(self, symbol: str, days: int = 30) -> Tuple[List, List]:
        """Get price history for a specific position"""
        if self.use_mock:
            return self._mock_position_history(symbol, days)
        
        try:
            # Get historical stock metrics for the symbol
            if self.db_manager:
                cursor = self.db_manager.conn.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        price
                    FROM stock_metrics 
                    WHERE symbol = ? 
                    AND created_at >= date('now', '-{} days')
                    ORDER BY created_at
                """.format(days), (symbol,))
            else:
                cursor = self.connection.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        price
                    FROM stock_metrics 
                    WHERE symbol = ? 
                    AND created_at >= date('now', '-{} days')
                    ORDER BY created_at
                """.format(days), (symbol,))
            
            results = cursor.fetchall()
            
            if not results:
                return self._mock_position_history(symbol, days)
            
            dates = [datetime.strptime(r[0], '%Y-%m-%d') if isinstance(r[0], str) else r[0] for r in results]
            prices = [float(r[1]) if r[1] else 0.0 for r in results]
            
            return dates, prices
            
        except Exception as e:
            print(f"Error fetching position history for {symbol}: {e}")
            return self._mock_position_history(symbol, days)
    
    def get_position_details(self, symbol: str) -> Optional[Dict]:
        """Get detailed info for a single position"""
        if self.use_mock:
            positions = self._mock_positions()
            return next((p for p in positions if p['symbol'] == symbol), None)
        
        try:
            if self.db_manager:
                cursor = self.db_manager.conn.execute("""
                    SELECT * FROM position_tracking WHERE symbol = ? AND status = 'OPEN'
                """, (symbol,))
            else:
                cursor = self.connection.execute("""
                    SELECT * FROM position_tracking WHERE symbol = ? AND status = 'OPEN'
                """, (symbol,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
            
        except Exception as e:
            print(f"Error fetching details for {symbol}: {e}")
            positions = self._mock_positions()
            return next((p for p in positions if p['symbol'] == symbol), None)
    
    def get_market_regime(self) -> Dict:
        """Get current market regime information"""
        try:
            if self.regime_detector:
                return self.regime_detector.get_current_regime()
            else:
                return {
                    'regime': 'neutral',
                    'fear_greed_value': 50,
                    'strategy': 'balanced',
                    'timestamp': datetime.now()
                }
        except Exception as e:
            print(f"Error getting market regime: {e}")
            return {
                'regime': 'unknown',
                'fear_greed_value': 50,
                'strategy': 'cautious',
                'timestamp': datetime.now()
            }
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent TradingAgents signals"""
        if self.use_mock:
            return self._mock_recent_signals(limit)
        
        try:
            if self.db_manager:
                cursor = self.db_manager.conn.execute("""
                    SELECT 
                        symbol, 
                        decision, 
                        conviction_score,
                        analysis_date,
                        entry_price,
                        regime
                    FROM tradingagents_analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            else:
                cursor = self.connection.execute("""
                    SELECT 
                        symbol, 
                        decision, 
                        conviction_score,
                        analysis_date,
                        entry_price,
                        regime
                    FROM tradingagents_analysis_results 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error fetching recent signals: {e}")
            return self._mock_recent_signals(limit)
    
    def get_portfolio_history(self, days: int = 30) -> Tuple[List, List]:
        """Get portfolio history - wrapper for get_portfolio_value_history"""
        return self.get_portfolio_value_history(days)
    
    def get_system_metrics(self) -> Dict:
        """Get system performance metrics"""
        try:
            positions = self.get_portfolio_positions()
            total_positions = len(positions)
            total_pnl = sum(p.get('unrealized_pnl', 0) for p in positions)
            total_value = sum(p.get('shares', 0) * p.get('current_price', 0) for p in positions)
            
            return {
                'total_positions': total_positions,
                'total_pnl': total_pnl,
                'total_value': total_value,
                'avg_pnl_pct': (total_pnl / total_value * 100) if total_value > 0 else 0,
                'last_updated': datetime.now()
            }
        except Exception as e:
            print(f"Error calculating system metrics: {e}")
            return {
                'total_positions': 0,
                'total_pnl': 0,
                'total_value': 0,
                'avg_pnl_pct': 0,
                'last_updated': datetime.now()
            }
    
    # Mock data methods for testing
    def _mock_positions(self) -> List[Dict]:
        """Generate mock positions for testing"""
        positions = [
            {
                'symbol': 'AAPL',
                'shares': 100,
                'entry_price': 175.50,
                'current_price': 182.30,
                'stop_loss': 170.00,
                'target_price': 195.00,
                'unrealized_pnl': 680.00,
                'pnl_percentage': 3.87
            },
            {
                'symbol': 'NVDA',
                'shares': 50,
                'entry_price': 480.25,
                'current_price': 465.80,
                'stop_loss': 450.00,
                'target_price': 520.00,
                'unrealized_pnl': -722.50,
                'pnl_percentage': -3.01
            },
            {
                'symbol': 'SPY',
                'shares': 200,
                'entry_price': 452.10,
                'current_price': 458.75,
                'stop_loss': 445.00,
                'target_price': 470.00,
                'unrealized_pnl': 1330.00,
                'pnl_percentage': 1.47
            }
        ]
        return positions
    
    def _mock_portfolio_history(self, days: int) -> Tuple[List, List]:
        """Generate mock portfolio history"""
        dates = []
        values = []
        base_value = 100000
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            dates.append(date)
            # Random walk
            change = random.uniform(-0.02, 0.025)
            base_value = base_value * (1 + change)
            values.append(base_value)
        
        return dates, values
    
    def _mock_position_history(self, symbol: str, days: int) -> Tuple[List, List]:
        """Generate mock price history for a position"""
        dates = []
        prices = []
        
        # Get current price from mock positions
        positions = self._mock_positions()
        position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if not position:
            return [], []
        
        current_price = position['current_price']
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            dates.append(date)
            # Random walk backwards from current price
            variance = 0.02 * (days - i) / days
            price = current_price * (1 + random.uniform(-variance, variance))
            prices.append(price)
        
        return dates, prices
    
    def _mock_recent_signals(self, limit: int) -> List[Dict]:
        """Generate mock recent signals"""
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'META', 'SPY', 'QQQ']
        decisions = ['BUY_STRONG', 'BUY_WEAK', 'HOLD', 'SELL_WEAK', 'SELL_STRONG']
        regimes = ['extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed']
        
        signals = []
        for i in range(limit):
            signal_date = datetime.now() - timedelta(days=i)
            signals.append({
                'symbol': random.choice(symbols),
                'decision': random.choice(decisions),
                'conviction_score': round(random.uniform(0.3, 0.95), 2),
                'analysis_date': signal_date,
                'entry_price': round(random.uniform(50, 500), 2),
                'regime': random.choice(regimes)
            })
        
        return signals
