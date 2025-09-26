"""
Data fetcher for KHAZAD_DUM monitoring
Interfaces with the existing database or provides mock data for testing
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

from config import DB_CONFIG, USE_MOCK_DATA, HISTORY_DAYS

# Try to import psycopg2, but it's optional for mock mode
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("Note: psycopg2 not installed. Database connections disabled, using mock data only.")


class DataFetcher:
    def __init__(self):
        self.connection = None
        self.use_mock = USE_MOCK_DATA
        if not self.use_mock:
            try:
                self.connect_db()
            except Exception as e:
                print(f"Database connection failed: {e}")
                print("Falling back to mock data...")
                self.use_mock = True
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        if not HAS_PSYCOPG2:
            raise ImportError("psycopg2 not installed")
        self.connection = psycopg2.connect(**DB_CONFIG)
    
    def get_cursor(self, dict_cursor=True):
        """Get a database cursor"""
        if dict_cursor and HAS_PSYCOPG2:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        else:
            return self.connection.cursor()
        
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def get_portfolio_positions(self) -> List[Dict]:
        """Get all current positions"""
        if self.use_mock:
            return self._mock_positions()
        
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute("""
                SELECT 
                    symbol,
                    shares,
                    entry_price,
                    current_price,
                    stop_loss,
                    target_price,
                    (current_price - entry_price) * shares as unrealized_pnl,
                    ((current_price - entry_price) / entry_price * 100) as pnl_percentage
                FROM positions
                WHERE shares > 0
                ORDER BY symbol
            """)
            return cursor.fetchall()
    
    def get_portfolio_value_history(self, days: int = HISTORY_DAYS) -> Tuple[List, List]:
        """Get portfolio value history"""
        if self.use_mock:
            return self._mock_portfolio_history(days)
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT date, total_value 
                FROM portfolio_history 
                WHERE date >= NOW() - INTERVAL '%s days'
                ORDER BY date
            """, (days,))
            results = cursor.fetchall()
            dates = [r[0] for r in results]
            values = [r[1] for r in results]
            return dates, values
    
    def get_position_history(self, symbol: str, days: int = HISTORY_DAYS) -> Tuple[List, List]:
        """Get price history for a specific position"""
        if self.use_mock:
            return self._mock_position_history(symbol, days)
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT date, close_price 
                FROM price_history 
                WHERE symbol = %s 
                AND date >= NOW() - INTERVAL '%s days'
                ORDER BY date
            """, (symbol, days))
            results = cursor.fetchall()
            dates = [r[0] for r in results]
            prices = [r[1] for r in results]
            return dates, prices
    
    def get_position_details(self, symbol: str) -> Dict:
        """Get detailed info for a single position"""
        if self.use_mock:
            positions = self._mock_positions()
            return next((p for p in positions if p['symbol'] == symbol), None)
        
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute("""
                SELECT * FROM positions WHERE symbol = %s
            """, (symbol,))
            return cursor.fetchone()
    
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
