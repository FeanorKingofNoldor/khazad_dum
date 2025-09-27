#!/usr/bin/env python3
"""
███████╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██╔════╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
██║     ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██║     ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
╚██████╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: Main Trading Pipeline                                                   │
│ 📄 FILE: main.py                                                                   │
│ 📅 CREATED: 2024-12-21                                                             │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ Main entry point orchestrating the complete 6-stage trading pipeline              │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - Market data APIs (Finnhub, yfinance)                                            │
│ - TradingAgents LLM framework                                                      │
│ - PostgreSQL database                                                              │
│ - Redis cache                                                                      │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: Complete Pipeline Orchestration                        │
│ └── 1. Market Regime Detection                                                     │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation                                                     │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - Requires valid API keys in .env file                                            │
│ - Database must be initialized before first run                                   │
│ - Pattern analysis runs weekly on configured day                                  │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - Full pipeline execution: 2-5 minutes for S&P 500                               │
│ - Memory usage: ~500MB peak during analysis                                       │
│ - API calls: ~100-500 depending on market conditions                             │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_main.py                                             │
│ - Integration Tests: tests/integration/test_full_pipeline.py                      │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Usage Guide: docs/guides/MAIN_PIPELINE_USAGE.md                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""

# Main script with Portfolio Constructor integration and Performance Observer
# ENHANCED with optional Pattern-Based Feedback System

import sys
import os
from datetime import datetime
import logging
from typing import Optional, Dict, Any

# Import structured logging configuration
from config.logging.logging_config import (
    setup_logging, 
    get_trading_logger,
    log_trading_decision,
    log_performance_metric,
    log_security_event
)

# Setup structured logging
if not setup_logging():
    # Fallback logging if structured setup fails
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Get specialized trading logger
logger = get_trading_logger('main', {'component': 'main_workflow'})

from src.core.market_analysis.regime_detector import RegimeDetector
from src.data_pipeline.storage.database_manager import DatabaseManager
from src.data_pipeline.market_data.stock_data_fetcher import StockDataFetcher
from src.core.stock_screening.stock_filter import StockFilter
from src.trading_engines.tradingagents_integration.batch_processor import BatchProcessor
from src.core.portfolio_management.position_tracker import PositionTracker
from src.core.portfolio_management.performance_observer import PerformanceObserver
from config.settings.base_config import PATTERN_WEEKLY_ANALYSIS_DAY



def initialize_components() -> Optional[Dict[str, Any]]:
    """
    Initialize all system components with proper error handling
    Returns dict of components or None if critical failure
    """
    components = {}
    
    try:
        logger.info("Initializing database manager...")
        components['database'] = DatabaseManager()
        
        logger.info("Initializing regime detector...")
        components['regime_detector'] = RegimeDetector()
        
        logger.info("Initializing stock data fetcher...")
        components['fetcher'] = StockDataFetcher()
        
        logger.info("Initializing stock filter...")
        components['filter_engine'] = StockFilter(components['database'])
        
        logger.info("Initializing batch processor...")
        components['batch_processor'] = BatchProcessor(components['database'])
        
        logger.info("Initializing position tracker...")
        components['position_tracker'] = PositionTracker(components['database'].conn)
        
        logger.info("Initializing performance observer...")
        components['observer'] = PerformanceObserver(components['database'].conn)
        
        logger.info("All components initialized successfully")
        return components
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        # Cleanup any partially initialized components
        for component in components.values():
            if hasattr(component, 'close'):
                try:
                    component.close()
                except:
                    pass
        return None


def validate_portfolio_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize portfolio context
    """
    validated = {
        'cash_available': max(0, context.get('cash_available', 100000)),
        'total_positions': max(0, context.get('total_positions', 0)),
        'unrealized_pnl_pct': context.get('unrealized_pnl_pct', 0)
    }
    
    # Sanity checks
    if validated['cash_available'] > 10_000_000:  # $10M limit
        logger.warning(f"Cash available seems high: ${validated['cash_available']:,.0f}")
    
    return validated


def main() -> int:
    """
    Complete KHAZAD_DUM workflow with robust error handling
    Returns exit code: 0 for success, 1 for failure
    """
    print(
        """
 /$$   /$$ /$$                                           /$$       /$$$$$$$                         
| $$  /$$/| $$                                          | $$      | $$__  $$                        
| $$ /$$/ | $$$$$$$   /$$$$$$  /$$$$$$$$  /$$$$$$   /$$$$$$$      | $$  \ $$ /$$   /$$ /$$$$$$/$$$$ 
| $$$$$/  | $$__  $$ |____  $$|____ /$$/ |____  $$ /$$__  $$      | $$  | $$| $$  | $$| $$_  $$_  $$
| $$  $$  | $$  \ $$  /$$$$$$$   /$$$$/   /$$$$$$$| $$  | $$      | $$  | $$| $$  | $$| $$ \ $$ \ $$
| $$\  $$ | $$  | $$ /$$__  $$  /$$__/   /$$__  $$| $$  | $$      | $$  | $$| $$  | $$| $$ | $$ | $$
| $$ \  $$| $$  | $$|  $$$$$$$ /$$$$$$$$|  $$$$$$$|  $$$$$$$      | $$$$$$$/|  $$$$$$/| $$ | $$ | $$
|__/  \__/|__/  |__/ \_______/|________/ \_______/ \_______/      |_______/  \______/ |__/ |__/ |__/
                                                                                                    
                                                                                                    
                                     _,-----------._       
                                 _,-'_,-----------._`-._    
                               ,'_,-'  ___________  `-._`.
                             ,','  _,-'___________`-._  `.`.
                           ,','  ,'_,-'     *     `-._`.  `.`.
                           /,'  ,','    *   |   *     `.`.  `.\
                         //  ,','     *    ,^.    *     `.`.  \\
                        //  /,'     *     / | \     *     `.\  \\
                       //  //            \/\^/\/            \\  \\
                      ;;  ;;              `---'              ::  ::
                      ||  ||              (___)              ||  ||
                     _||__||_            ,'----.            _||__||_
                    (o.____.o)____        `---'        ____(o.____.o)
                      |    | /,--.)                   (,--.\ |    |
                      |    |((  -`___               ___`   ))|    |
                      |    | \\,'',  `.           .'  .``.// |    |
                      |    |  // (___,'.         .'.___) \\  |    |
                     /|    | ;;))  ____) .     . (____  ((\\ |    |\
                     \|.__ | ||/ .'.--.\/       `/,--.`. \;: | __,|;
                      |`-,`;.| :/ /,'  `)-'   `-('  `.\ \: |.;',-'|
                      |   `..  ' / \__.'         `.__/ \ `  ,.'   |
                      |    |,\  /,                     ,\  /,|    |
                      |    ||: : )          .          ( : :||    |
                     /|    |:; |/  .      ./|\,      ,  \| :;|    |\
                     \|.__ |/  :  ,/-   <------->   ,\.  ;  \| __,|;
                      |`-.``:   `'/-.     '\|/`     ,-\`;   ;'',-'|
                      |   `..   ,' `'       '       `  `.   ,.'   |
                      |    ||  :                         :  ||    |
                      |    ||  |                         |  ||    |
                      |    ||  |                         |  ||    |
                      |    |'  |            _            |  `|    |
                      |    |   |          '|))           |   |    |
                      ;____:   `._        `'           _,'   ;____:
                     {______}     \___________________/     {______}
                     |______|_______________________________|______|
                                                                                                    
    """
    )
    
    logger.info("Starting KHAZAD_DUM trading system")
    
    try:
        # Initialize components
        components = initialize_components()
        if not components:
            logger.error("Critical: Failed to initialize system components")
            return 1

        # Extract components for cleaner code
        database = components['database']
        regime_detector = components['regime_detector']
        fetcher = components['fetcher']
        filter_engine = components['filter_engine']
        batch_processor = components['batch_processor']
        position_tracker = components['position_tracker']
        observer = components['observer']

        # Step 1: Detect regime with error handling
        logger.info("Step 1: Detecting Market Regime...")
        regime = regime_detector.get_current_regime()
        if not regime or 'regime' not in regime:
            logger.error("Failed to detect market regime")
            return 1
        
        # Log regime to database
        if not database.log_regime(regime):
            logger.warning("Failed to log regime to database")
        
        print(f"\n1. Market Regime Detection Complete")
        print(f"   Regime: {regime['regime']}")
        print(f"   CNN F&G: {regime.get('fear_greed_value', 'N/A')}")
        print(f"   Strategy: {regime.get('strategy', 'N/A')}")

        # Step 2: Fetch data with error handling
        logger.info("Step 2: Fetching S&P 500 Data...")
        try:
            metrics = fetcher.fetch_all_sp500()
            if metrics.empty:
                logger.error("No stock data retrieved")
                return 1
            
            rows_inserted = database.insert_stock_metrics(metrics)
            print(f"\n2. Stock Data Fetch Complete")
            print(f"   ✓ Fetched {len(metrics)} stocks")
            print(f"   ✓ Inserted {rows_inserted} records")
            
        except Exception as e:
            logger.error(f"Failed to fetch stock data: {e}")
            return 1

        # Step 3: Filter with validation
        logger.info("Step 3: Running 3-Layer Filter...")
        try:
            candidates = filter_engine.run_full_filter(regime)
            if candidates is None or candidates.empty:
                logger.warning("No candidates passed filtering")
                print(f"\n3. Stock Filtering Complete")
                print(f"   ⚠ No candidates passed filtering criteria")
                print(f"\n✓ KHAZAD_DUM run completed (no trades generated)")
                return 0  # Not an error, just no opportunities
            
            print(f"\n3. Stock Filtering Complete")
            print(f"   ✓ Selected {len(candidates)} candidates")
            
        except Exception as e:
            logger.error(f"Failed during filtering: {e}")
            return 1

        # Generate batch ID for this run
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Generated batch ID: {batch_id}")

        # Record filter decisions in observer
        try:
            for _, row in candidates.iterrows():
                observer.record_pipeline_decision(
                    batch_id=batch_id,
                    symbol=row["symbol"],
                    stage="filter",
                    data={
                        "passed": True,
                        "score": row.get("score", 0),
                        "layer": "final",
                        "rsi_2": row.get("rsi_2", 0),
                        "volume_ratio": row.get("volume_ratio", 1),
                        "regime": regime["regime"],
                    },
                )
        except Exception as e:
            logger.warning(f"Failed to record filter decisions: {e}")

        # Step 4: Get portfolio context
        logger.info("Step 4: Getting Portfolio Context...")
        portfolio_context = validate_portfolio_context({
            "cash_available": 100000,  # TODO: Get from IBKR
            "total_positions": 0,
            "unrealized_pnl_pct": 0,
        })
        print(f"\n4. Portfolio Context")
        print(f"   Cash Available: ${portfolio_context['cash_available']:,.0f}")

        # Step 5: Process through TradingAgents and Portfolio Constructor
        logger.info("Step 5: Running TradingAgents Analysis...")
        try:
            result = batch_processor.process_batch(
                candidates=candidates,
                regime_data=regime,
                portfolio_context=portfolio_context,
            )
            
            if not result.get("success"):
                logger.error(f"Batch processing failed: {result.get('error', 'Unknown error')}")
                return 1
            
            # Log pattern system status if available
            if result.get("patterns_enabled"):
                print("   ✓ Pattern-based feedback enabled")
                logger.info("Pattern system is active")
                
        except Exception as e:
            logger.error(f"Failed during TradingAgents analysis: {e}")
            return 1
        # Generate batch ID for this run (original)
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Record filter decisions in observer (original)
        for _, row in candidates.iterrows():
            observer.record_pipeline_decision(
                batch_id=batch_id,
                symbol=row["symbol"],
                stage="filter",
                data={
                    "passed": True,
                    "score": row["score"],
                    "layer": "final",
                    "rsi_2": row["rsi_2"],
                    "volume_ratio": row["volume_ratio"],
                    "regime": regime["regime"],
                },
            )

        # Step 4: Get portfolio context (original)
        print("\n4. Getting Portfolio Context...")
        portfolio_context = {
            "cash_available": 100000,  # Replace with IBKR data
            "total_positions": 0,
            "unrealized_pnl_pct": 0,
        }

        # Step 5: Process through TradingAgents and Portfolio Constructor (original)
        print("\n5. Running TradingAgents Analysis...")
        result = batch_processor.process_batch(
            candidates=candidates,
            regime_data=regime,
            portfolio_context=portfolio_context,
        )
        
        # ADD: Note if patterns are enabled
        if result.get("patterns_enabled"):
            print("   ✓ Pattern-based feedback enabled")

        # Record TradingAgents decisions in observer
        try:
            if result.get("success"):
                # Get the actual analysis results from database
                analysis_results = database.conn.execute(
                    """
                    SELECT symbol, decision, conviction_score
                    FROM tradingagents_analysis_results
                    WHERE batch_id = ?
                """,
                    (result["batch_id"],),
                ).fetchall()

                for symbol, decision, conviction in analysis_results:
                    observer.record_pipeline_decision(
                        batch_id=batch_id,
                        symbol=symbol,
                        stage="tradingagents",
                        data={"decision": decision, "conviction": conviction},
                    )

                # Record portfolio constructor selections
                for stock in result.get("selections", []):
                    observer.record_pipeline_decision(
                        batch_id=batch_id,
                        symbol=stock["symbol"],
                        stage="portfolio_constructor",
                        data={"selected": True},
                    )

                for stock in result.get("excluded", []):
                    observer.record_pipeline_decision(
                        batch_id=batch_id,
                        symbol=stock["symbol"],
                        stage="portfolio_constructor",
                        data={"selected": False},
                    )
        except Exception as e:
            logger.warning(f"Failed to record pipeline decisions: {e}")
        if result.get("success"):
            # Get the actual analysis results from database
            analysis_results = database.conn.execute(
                """
                SELECT symbol, decision, conviction_score
                FROM tradingagents_analysis_results
                WHERE batch_id = ?
            """,
                (result["batch_id"],),
            ).fetchall()

            for symbol, decision, conviction in analysis_results:
                observer.record_pipeline_decision(
                    batch_id=batch_id,
                    symbol=symbol,
                    stage="tradingagents",
                    data={"decision": decision, "conviction": conviction},
                )

            # Record portfolio constructor selections (original)
            for stock in result.get("selections", []):
                observer.record_pipeline_decision(
                    batch_id=batch_id,
                    symbol=stock["symbol"],
                    stage="portfolio_constructor",
                    data={"selected": True},
                )

            for stock in result.get("excluded", []):
                observer.record_pipeline_decision(
                    batch_id=batch_id,
                    symbol=stock["symbol"],
                    stage="portfolio_constructor",
                    data={"selected": False},
                )

        # Display results
        print(f"\n{'='*60}")
        print("PORTFOLIO CONSTRUCTION COMPLETE")
        print(f"{'='*60}")
        print(f"Batch ID: {result.get('batch_id', 'Unknown')}")
        print(f"Total Analyzed: {result.get('total_analyzed', 0)}")
        print(f"BUY Signals: {result.get('buy_signals', 0)}")
        
        selections = result.get('selections', [])
        print(f"\nFINAL SELECTIONS ({len(selections)}):")
        
        if selections:
            for i, stock in enumerate(selections, 1):
                print(f"   {i}. {stock.get('symbol', 'N/A')}")
                print(f"      Position: {stock.get('position_size_pct', 0)}% (${stock.get('position_size_dollars', 0):,.0f})")
                print(f"      Conviction: {stock.get('conviction_score', 0):.1f}")
                print(f"      Entry: ${stock.get('entry_price', 0):.2f}")
                print(f"      Stop: ${stock.get('stop_loss', 0):.2f}")
                print(f"      Target: ${stock.get('target_price', 0):.2f}")
                print(f"      Reason: {stock.get('selection_reason', 'N/A')}")
                
                # Record execution intent
                try:
                    observer.record_pipeline_decision(
                        batch_id=batch_id,
                        symbol=stock.get("symbol", ""),
                        stage="execution",
                        data={"entry_price": stock.get("entry_price", 0), "regime": regime["regime"]},
                    )
                except Exception as e:
                    logger.warning(f"Failed to record execution decision: {e}")
        else:
            print("   No positions selected for entry")
        print(f"\n{'='*60}")
        print("PORTFOLIO CONSTRUCTION COMPLETE")
        print(f"{'='*60}")
        print(f"Batch ID: {result['batch_id']}")
        print(f"Total Analyzed: {result['total_analyzed']}")
        print(f"BUY Signals: {result['buy_signals']}")
        print(f"\nFINAL SELECTIONS ({len(result['selections'])}):")

        for i, stock in enumerate(result["selections"], 1):
            print(f"   {i}. {stock['symbol']}")
            print(
                f"      Position: {stock['position_size_pct']}% (${stock['position_size_dollars']:,.0f})"
            )
            print(f"      Conviction: {stock['conviction_score']:.1f}")
            print(f"      Entry: ${stock['entry_price']:.2f}")
            print(f"      Stop: ${stock['stop_loss']:.2f}")
            print(f"      Target: ${stock['target_price']:.2f}")
            print(f"      Reason: {stock.get('selection_reason', 'N/A')}")

            # Record execution intent (original)
            observer.record_pipeline_decision(
                batch_id=batch_id,
                symbol=stock["symbol"],
                stage="execution",
                data={"entry_price": stock["entry_price"], "regime": regime["regime"]},
            )

        # Step 6: Update existing positions
        logger.info("Step 6: Updating Open Positions...")
        try:
            position_tracker.update_positions(check_exits=True)
            print("\n6. Position Updates Complete")
        except Exception as e:
            logger.error(f"Failed to update positions: {e}")
            # Don't return error here as this is not critical for new analysis
        
        # Step 7: Pattern system processing (if available)
        try:
            closed_positions = database.conn.execute("""
                SELECT * FROM position_tracking 
                WHERE exit_date = date('now') AND pattern_id IS NOT NULL
            """).fetchall()
            
            if closed_positions:
                logger.info(f"Processing {len(closed_positions)} closed positions for pattern learning")
                memories_injected = batch_processor.process_closed_positions(
                    [dict(pos) for pos in closed_positions]
                )
                print(f"   ✓ Injected {memories_injected} memories from closed trades")
                
        except Exception as e:
            logger.debug(f"Pattern processing not available or failed: {e}")
            # This is optional functionality, don't fail the main process
        
        # Step 8: Analyze performance feedback
        logger.info("Step 7: Analyzing Performance Feedback...")
        try:
            feedback = position_tracker.analyze_feedback(lookback_days=30)
            
            if "selected_avg_return" in feedback:
                print(f"\n7. Performance Analysis")
                print(f"   Selected Avg Return: {feedback['selected_avg_return']:.2f}%")
                print(f"   Excluded Avg Return: {feedback['excluded_avg_return']:.2f}%")
                print(f"   Selection Edge: {feedback['selection_edge']:.2f}%")
            else:
                print(f"\n7. Performance Analysis")
                print(f"   {feedback.get('message', 'No recent data available')}")
                
        except Exception as e:
            logger.warning(f"Performance feedback analysis failed: {e}")
        
        # Step 9: Show observation summary
        logger.info("Step 8: Generating Observation Summary...")
        try:
            print("\n8. Observation Summary")
            observer.print_observation_summary()
        except Exception as e:
            logger.warning(f"Failed to generate observation summary: {e}")
        
        # Weekly pattern analysis (if applicable)
        if datetime.now().weekday() == PATTERN_WEEKLY_ANALYSIS_DAY:
            logger.info("Running weekly pattern analysis...")
            try:
                pattern_results = batch_processor.run_weekly_pattern_analysis()
                if 'error' not in pattern_results:
                    print("\n9. Weekly Pattern Analysis Complete")
                    print(f"   ✓ Pattern analysis complete")
            except Exception as e:
                logger.debug(f"Weekly pattern analysis not available: {e}")
        
        print("\n✓ KHAZAD_DUM Portfolio Construction Complete!")
        logger.info("Trading system run completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
        print("\n⚠ System interrupted by user")
        return 130  # Standard Unix exit code for SIGINT
    
    except Exception as e:
        logger.error(f"Unexpected error in main workflow: {e}", exc_info=True)
        print(f"\n❌ System error: {e}")
        return 1
        
    finally:
        # Cleanup resources
        logger.info("Cleaning up resources...")
        try:
            if 'components' in locals() and components:
                for component_name, component in components.items():
                    if hasattr(component, 'close'):
                        try:
                            component.close()
                            logger.debug(f"Closed {component_name}")
                        except Exception as e:
                            logger.warning(f"Error closing {component_name}: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        print("\n6. Updating Open Positions...")
        position_tracker.update_positions(check_exits=True)
        
        # ADD: Close positions with pattern learning if available
        try:
            closed_positions = database.conn.execute("""
                SELECT * FROM position_tracking 
                WHERE exit_date = date('now') AND pattern_id IS NOT NULL
            """).fetchall()
            
            for pos in closed_positions:
                batch_processor.close_position_with_learning(dict(pos))
        except:
            pass  # Pattern fields might not exist
        
        # Check for recently closed positions
        closed_today = database.conn.execute("""
            SELECT * FROM position_tracking 
            WHERE exit_date = date('now') 
            AND pattern_id IS NOT NULL
        """).fetchall()

        if closed_today:
            print(f"\n   Processing {len(closed_today)} closed positions...")
            memories_injected = batch_processor.process_closed_positions(
                [dict(pos) for pos in closed_today]
            )
            print(f"   ✓ Injected {memories_injected} memories from closed trades")

        # Step 8: Analyze feedback (original)
        print("\n7. Analyzing Performance Feedback...")
        feedback = position_tracker.analyze_feedback(lookback_days=30)

        if "selected_avg_return" in feedback:
            print(f"   Selected Avg Return: {feedback['selected_avg_return']:.2f}%")
            print(f"   Excluded Avg Return: {feedback['excluded_avg_return']:.2f}%")
            print(f"   Selection Edge: {feedback['selection_edge']:.2f}%")

        # Step 9: Show observation summary (original)
        print("\n8. Observation Summary...")
        observer.print_observation_summary()
        
        # ADD: Weekly pattern analysis on Sundays (if available)
        if datetime.now().weekday() == PATTERN_WEEKLY_ANALYSIS_DAY:
            print("\n9. Weekly Pattern Analysis...")
            try:
                pattern_results = batch_processor.run_weekly_pattern_analysis()
                if 'error' not in pattern_results:
                    print(f"   ✓ Pattern analysis complete")
            except Exception as e:
                logger.debug(f"Weekly pattern analysis not available: {e}")

    print("\n✓ KHAZAD_DUM Portfolio Construction Complete!")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
