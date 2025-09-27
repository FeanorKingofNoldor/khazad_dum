"""
Position Tracking Module
Tracks actual performance for feedback loop
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import yfinance as yf
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PositionTracker:
    """
    Tracks positions after entry for performance analysis
    Enhanced with safe calculations and validation
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safely divide two numbers, handling zero denominator"""
        if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
            return default
        if np.isnan(numerator) or np.isinf(numerator):
            return default
        
        result = numerator / denominator
        return result if np.isfinite(result) else default
    
    @staticmethod
    def _safe_multiply(a: float, b: float, default: float = 0.0) -> float:
        """Safely multiply two numbers, handling NaN/inf"""
        if any(np.isnan(x) or np.isinf(x) for x in [a, b]):
            return default
        
        result = a * b
        return result if np.isfinite(result) else default
    
    @staticmethod
    def _validate_price(price: Union[float, int], name: str = "price") -> float:
        """Validate price value is positive and finite"""
        if price is None:
            raise ValueError(f"{name} cannot be None")
        
        price = float(price)
        if not np.isfinite(price):
            raise ValueError(f"{name} must be finite, got {price}")
        
        if price <= 0:
            raise ValueError(f"{name} must be positive, got {price}")
        
        return price
    
    @contextmanager
    def _db_transaction(self):
        """Database transaction context manager"""
        try:
            yield self.db
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Transaction failed, rolling back: {e}")
            self.db.rollback()
            raise
    
    def enter_positions(self, batch_id: str, selections: List[Dict]) -> bool:
        """
        Record position entries in tracking table with validation
        Returns True if successful
        """
        if not batch_id or not batch_id.strip():
            raise ValueError("batch_id cannot be empty")
        
        if not selections:
            self.logger.warning("No selections provided for position tracking")
            return True
        
        try:
            with self._db_transaction():
                for i, stock in enumerate(selections):
                    try:
                        # Validate required fields
                        symbol = stock.get('symbol', '').strip().upper()
                        if not symbol:
                            raise ValueError(f"Selection {i}: symbol cannot be empty")
                        
                        entry_price = self._validate_price(stock.get('entry_price', 0), "entry_price")
                        shares = max(0, int(stock.get('shares', 0)))
                        position_value = max(0, float(stock.get('position_size_dollars', 0)))
                        conviction = max(0, min(100, float(stock.get('conviction_score', 0))))
                        
                        # Sanity check: position value should roughly equal shares * price
                        if shares > 0 and position_value > 0:
                            expected_value = self._safe_multiply(shares, entry_price)
                            value_diff = abs(position_value - expected_value) / max(position_value, expected_value)
                            if value_diff > 0.1:  # 10% tolerance
                                self.logger.warning(
                                    f"Position value mismatch for {symbol}: "
                                    f"expected ~${expected_value:.2f}, got ${position_value:.2f}"
                                )
                        
                        self.db.execute("""
                        INSERT INTO position_tracking
                        (batch_id, symbol, entry_date, entry_price, shares, 
                         position_value, was_selected, tradingagents_conviction, regime_at_entry)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            batch_id,
                            symbol,
                            datetime.now().date(),
                            entry_price,
                            shares,
                            position_value,
                            1,  # was_selected = True
                            conviction,
                            stock.get('regime', 'Unknown')
                        ))
                        
                    except Exception as e:
                        self.logger.error(f"Failed to insert position {i} ({stock.get('symbol', 'unknown')}): {e}")
                        raise
                
                # Also track excluded BUY signals for comparison
                try:
                    self._track_excluded_positions(batch_id)
                except Exception as e:
                    self.logger.warning(f"Failed to track excluded positions: {e}")
                    # Don't fail the entire operation for this
            
            self.logger.info(f"Successfully entered {len(selections)} positions for tracking")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enter positions: {e}")
            return False
    
    def _track_excluded_positions(self, batch_id: str):
        """Track excluded BUY signals for regret analysis"""
        query = """
        SELECT symbol, conviction_score, entry_price, regime
        FROM tradingagents_analysis_results
        WHERE batch_id = ? AND decision = 'BUY'
        AND symbol NOT IN (
            SELECT symbol FROM portfolio_selections
            WHERE batch_id = ? AND selected = 1
        )
        """
        
        df = pd.read_sql(query, self.db, params=[batch_id, batch_id])
        
        for _, row in df.iterrows():
            self.db.execute("""
            INSERT INTO position_tracking
            (batch_id, symbol, entry_date, entry_price, 
             was_selected, tradingagents_conviction, regime_at_entry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                batch_id,
                row['symbol'],
                datetime.now().date(),
                row['entry_price'],
                0,  # was_selected = False
                row['conviction_score'],
                row['regime']
            ))
    
    def update_positions(self, check_exits: bool = True) -> Dict[str, int]:
        """
        Update all open positions with current prices
        Check for exit conditions if requested
        Returns dict with update counts
        """
        result = {'updated': 0, 'exited': 0, 'errors': 0}
        
        try:
            # Get open positions
            query = """
            SELECT * FROM position_tracking
            WHERE exit_date IS NULL AND status = 'OPEN'
            ORDER BY symbol
            """
            
            positions = pd.read_sql(query, self.db)
            
            if positions.empty:
                self.logger.info("No open positions to update")
                return result
            
            self.logger.info(f"Updating {len(positions)} open positions")
            
            for _, pos in positions.iterrows():
                try:
                    symbol = pos['symbol']
                    entry_price = self._validate_price(pos['entry_price'], "entry_price")
                    
                    # Get current data with timeout protection
                    ticker = yf.Ticker(symbol)
                    hist_data = ticker.history(period='2d')  # Get 2 days to ensure data
                    
                    if hist_data.empty:
                        self.logger.warning(f"No price data available for {symbol}")
                        result['errors'] += 1
                        continue
                    
                    current_price = float(hist_data['Close'].iloc[-1])
                    current_price = self._validate_price(current_price, "current_price")
                    
                    # Calculate performance with safe division
                    pnl_pct = self._safe_divide(
                        (current_price - entry_price) * 100, 
                        entry_price, 
                        default=0.0
                    )
                    
                    # Calculate holding days safely
                    entry_date = pos['entry_date']
                    if isinstance(entry_date, str):
                        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
                    
                    holding_days = (datetime.now().date() - entry_date).days
                    
                    # Check exit conditions
                    exit_triggered = False
                    exit_reason = None
                    
                    if check_exits:
                        try:
                            targets = self._get_exit_targets(pos['batch_id'], pos['symbol'])
                            
                            # Validate targets
                            stop_loss = targets.get('stop_loss', 0)
                            target_price = targets.get('target_price', float('inf'))
                            
                            if stop_loss > 0 and current_price <= stop_loss:
                                exit_triggered = True
                                exit_reason = 'stop_loss'
                            elif target_price > 0 and target_price != float('inf') and current_price >= target_price:
                                exit_triggered = True
                                exit_reason = 'target'
                            elif holding_days >= 10:  # Max holding period
                                exit_triggered = True
                                exit_reason = 'time_limit'
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to get exit targets for {symbol}: {e}")
                    
                    if exit_triggered:
                        success = self._exit_position(
                            pos['batch_id'],
                            pos['symbol'],
                            current_price,
                            exit_reason
                        )
                        if success:
                            result['exited'] += 1
                            self.logger.info(f"Exited {symbol}: {exit_reason} at ${current_price:.2f}")
                        else:
                            result['errors'] += 1
                    else:
                        # Just update metrics
                        success = self._update_position_metrics(
                            pos['batch_id'],
                            pos['symbol'],
                            pnl_pct,
                            holding_days,
                            current_price
                        )
                        if success:
                            result['updated'] += 1
                        else:
                            result['errors'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to update {pos.get('symbol', 'unknown')}: {e}")
                    result['errors'] += 1
            
            self.logger.info(
                f"Position update complete: {result['updated']} updated, "
                f"{result['exited']} exited, {result['errors']} errors"
            )
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update positions: {e}")
            result['errors'] = -1
            return result
    
    def _get_exit_targets(self, batch_id: str, symbol: str) -> Dict:
        """Get stop loss and target price from original analysis"""
        query = """
        SELECT stop_loss, target_price
        FROM tradingagents_analysis_results
        WHERE batch_id = ? AND symbol = ?
        """
        
        result = self.db.execute(query, (batch_id, symbol)).fetchone()
        if result:
            return {'stop_loss': result[0], 'target_price': result[1]}
        else:
            # Default fallback
            return {'stop_loss': 0, 'target_price': float('inf')}
    
    def _exit_position(
        self,
        batch_id: str,
        symbol: str,
        exit_price: float,
        exit_reason: str
    ) -> bool:
        """Record position exit with safe calculations"""
        try:
            exit_price = self._validate_price(exit_price, "exit_price")
            
            # Get entry data
            query = """
            SELECT entry_price, entry_date, shares, position_value
            FROM position_tracking
            WHERE batch_id = ? AND symbol = ? AND exit_date IS NULL
            """
            
            entry_data = self.db.execute(query, (batch_id, symbol)).fetchone()
            
            if not entry_data:
                self.logger.warning(f"No open position found for {symbol} in batch {batch_id}")
                return False
            
            entry_price, entry_date, shares, position_value = entry_data
            
            # Validate entry data
            entry_price = self._validate_price(entry_price, "entry_price")
            shares = max(0, int(shares or 0))
            position_value = max(0, float(position_value or 0))
            
            # Calculate holding days
            if isinstance(entry_date, str):
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            holding_days = (datetime.now().date() - entry_date).days
            
            # Safe P&L calculations
            pnl_dollars = self._safe_multiply((exit_price - entry_price), shares)
            pnl_percent = self._safe_divide((exit_price - entry_price) * 100, entry_price)
            
            # Determine performance category
            if pnl_percent > 3:
                category = 'winner'
            elif pnl_percent < -2:
                category = 'loser'
            else:
                category = 'neutral'
            
            # Update record with transaction safety
            with self._db_transaction():
                self.db.execute("""
                UPDATE position_tracking
                SET exit_date = ?, exit_price = ?, exit_reason = ?,
                    holding_days = ?, pnl_dollars = ?, pnl_percent = ?,
                    actual_performance_category = ?, closed_at = ?, status = 'CLOSED'
                WHERE batch_id = ? AND symbol = ? AND exit_date IS NULL
                """, (
                    datetime.now().date(),
                    exit_price,
                    exit_reason,
                    holding_days,
                    pnl_dollars,
                    pnl_percent,
                    category,
                    datetime.now(),
                    batch_id,
                    symbol
                ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to exit position {symbol}: {e}")
            return False
    
    def _update_position_metrics(
        self,
        batch_id: str,
        symbol: str,
        current_pnl_pct: float,
        holding_days: int,
        current_price: float
    ) -> bool:
        """Update position metrics without exiting"""
        try:
            # Validate inputs
            if not np.isfinite(current_pnl_pct):
                current_pnl_pct = 0.0
            
            current_price = self._validate_price(current_price, "current_price")
            holding_days = max(0, int(holding_days))
            
            # Track max gain/drawdown
            query = """
            SELECT max_gain_percent, max_drawdown_percent
            FROM position_tracking
            WHERE batch_id = ? AND symbol = ? AND exit_date IS NULL
            """
            
            result = self.db.execute(query, (batch_id, symbol)).fetchone()
            if not result:
                self.logger.warning(f"No open position found for metrics update: {symbol}")
                return False
            
            max_gain = max(result[0] or 0, current_pnl_pct)
            max_drawdown = min(result[1] or 0, current_pnl_pct)
            
            # Update with transaction safety
            with self._db_transaction():
                self.db.execute("""
                UPDATE position_tracking
                SET max_gain_percent = ?, max_drawdown_percent = ?, 
                    holding_days = ?, pnl_percent = ?
                WHERE batch_id = ? AND symbol = ? AND exit_date IS NULL
                """, (
                    max_gain, 
                    max_drawdown, 
                    holding_days, 
                    current_pnl_pct,
                    batch_id, 
                    symbol
                ))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metrics for {symbol}: {e}")
            return False
    
    def analyze_feedback(self, lookback_days: int = 30) -> Dict:
        """
        Analyze performance for feedback loop
        Compare selected vs excluded stocks
        """
        cutoff_date = datetime.now().date() - timedelta(days=lookback_days)
        
        # Get closed positions
        query = """
        SELECT 
            symbol,
            was_selected,
            tradingagents_conviction,
            pnl_percent,
            actual_performance_category,
            exit_reason
        FROM position_tracking
        WHERE exit_date >= ? AND exit_date IS NOT NULL
        """
        
        df = pd.read_sql(query, self.db, params=[cutoff_date])
        
        if df.empty:
            return {"message": "No closed positions to analyze"}
        
        # Calculate metrics
        selected = df[df['was_selected'] == 1]
        excluded = df[df['was_selected'] == 0]
        
        analysis = {
            "period_days": lookback_days,
            "total_positions": len(df),
            
            # Selected performance
            "selected_count": len(selected),
            "selected_avg_return": selected['pnl_percent'].mean() if len(selected) > 0 else 0,
            "selected_win_rate": (selected['actual_performance_category'] == 'winner').mean() if len(selected) > 0 else 0,
            
            # Excluded performance (what we missed)
            "excluded_count": len(excluded),
            "excluded_avg_return": excluded['pnl_percent'].mean() if len(excluded) > 0 else 0,
            "excluded_win_rate": (excluded['actual_performance_category'] == 'winner').mean() if len(excluded) > 0 else 0,
            
            # Regret analysis
            "selection_edge": (selected['pnl_percent'].mean() - excluded['pnl_percent'].mean()) if len(selected) > 0 and len(excluded) > 0 else 0
        }
        
        # Find best missed opportunity
        if len(excluded) > 0:
            best_excluded = excluded.nlargest(1, 'pnl_percent').iloc[0]
            analysis['best_missed'] = {
                "symbol": best_excluded['symbol'],
                "return": best_excluded['pnl_percent'],
                "conviction": best_excluded['tradingagents_conviction']
            }
        
        # Find worst selection
        if len(selected) > 0:
            worst_selected = selected.nsmallest(1, 'pnl_percent').iloc[0]
            analysis['worst_selected'] = {
                "symbol": worst_selected['symbol'],
                "return": worst_selected['pnl_percent'],
                "conviction": worst_selected['tradingagents_conviction']
            }
        
        # Save to feedback_analysis table
        self._save_feedback_analysis(analysis)
        
        return analysis
    
    def _save_feedback_analysis(self, analysis: Dict):
        """Save feedback analysis to database"""
        self.db.execute("""
        INSERT INTO feedback_analysis
        (analysis_date, selected_stocks_performance, excluded_buys_performance,
         selection_accuracy, tradingagents_accuracy, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().date(),
            analysis.get('selected_avg_return', 0),
            analysis.get('excluded_avg_return', 0),
            analysis.get('selected_win_rate', 0),
            analysis.get('selection_edge', 0),
            json.dumps(analysis)
        ))
        
        self.db.commit()

    def close_position_with_pattern_learning(self, position_id: int, exit_price: float, 
                                            exit_reason: str, pattern_wrapper=None):
        """
        Close position and trigger pattern learning
        Enhanced to inject both trade and pattern memories
        """
        # Get position data
        position = self.conn.execute("""
            SELECT * FROM position_tracking WHERE id = ?
        """, (position_id,)).fetchone()
        
        if not position:
            return False
        
        # Calculate P&L
        position_data = dict(position)
        position_data['exit_price'] = exit_price
        position_data['exit_reason'] = exit_reason
        position_data['exit_date'] = datetime.now().date()
        position_data['pnl_percent'] = ((exit_price - position_data['entry_price']) / 
                                        position_data['entry_price'] * 100)
        position_data['holding_days'] = (position_data['exit_date'] - 
                                        position_data['entry_date']).days
        
        # Update database
        self.conn.execute("""
            UPDATE position_tracking 
            SET exit_date = ?, exit_price = ?, exit_reason = ?,
                holding_days = ?, pnl_percent = ?, pnl_dollars = ?
            WHERE id = ?
        """, (
            position_data['exit_date'],
            exit_price,
            exit_reason,
            position_data['holding_days'],
            position_data['pnl_percent'],
            position_data['pnl_percent'] * position_data['position_value'] / 100,
            position_id
        ))
        self.conn.commit()
        
        # ENHANCED: Inject memories if pattern system available
        if pattern_wrapper and position_data.get('pattern_id'):
            try:
                # Update pattern performance
                pattern_wrapper.tracker.track_exit(
                    position_data['pattern_id'],
                    position_data
                )
                
                # Get updated pattern stats
                pattern_stats = pattern_wrapper.pattern_db.get_pattern_stats(
                    position_data['pattern_id']
                )
                
                # Inject both trade and pattern memories
                if pattern_stats:
                    pattern_wrapper.memory_injector.inject_closed_position_memories(
                        position_data, pattern_stats
                    )
                    logger.info(f"Injected hybrid memories for {position_data['symbol']}")
                    
            except Exception as e:
                logger.warning(f"Pattern memory injection failed: {e}")
        
        return True