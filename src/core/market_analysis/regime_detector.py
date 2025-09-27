#!/usr/bin/env python3
"""
██╗  ██╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██║ ██╔╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
█████╔╝ ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██╔═██╗ ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
██║  ██╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: Market Regime Detection                                              │
│ 📄 FILE: regime_detector.py                                                     │
│ 📅 CREATED: 2024-12-21                                                             │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ Stage 1: Classify market conditions using CNN Fear & Greed Index + VIX            │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - CNN Fear & Greed Index API                                                       │
│ - Yahoo Finance (VIX data)                                                         │
│ - Custom CNN scraper (Python 3.13 compatibility)                                 │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: 1. Market Regime Detection                           │
│ └── 1. Market Regime Detection ← YOU ARE HERE                                    │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation                                                     │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - Fallbacks to VIX-only regime when CNN feed fails                                │
│ - 300s cache duration to minimize API calls                                       │
│ - Extreme Fear = 1.5x positions, Extreme Greed = 0.5x positions                  │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - Cached regime calls: ~1ms response time                                         │
│ - Fresh regime calls: ~500ms (network dependent)                                  │
│ - VIX fallback: ~200ms                                                             │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_regime_detector.py                                  │
│ - Integration Tests: tests/integration/test_market_analysis_integration.py        │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Usage Guide: docs/guides/MARKET_REGIME_USAGE.md                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""

# Market Regime Detection using CNN Fear & Greed Index
# Using custom scraper for Python 3.13 compatibility

import time
import json
from datetime import datetime
from typing import Dict, Optional

import yfinance as yf

# Use our custom scraper instead
from src.core.market_analysis.cnn_feed_parser import CNNFeedParser

from config.settings.base_config import (
    REGIME_THRESHOLDS,
    POSITION_MULTIPLIERS,
    FILTER_PERCENTILES,
    EXPECTED_WIN_RATES,
    CACHE_DURATION,
)


class RegimeDetector:
    """
    Fetches market regime from professional sources
    """

    def __init__(self):
        self.cnn_client = CNNFeedParser()  # Our custom scraper
        self.cache = {}
        self.cache_duration = CACHE_DURATION
        self._last_regime = None  # Cache the complete regime
        self._last_regime_time = 0

    def get_current_regime(self, force_refresh: bool = False) -> Dict:
        """
        Main method - returns complete regime analysis
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
        """
        # Check if we have a recent cached regime (unless forced refresh)
        if not force_refresh and self._last_regime:
            if time.time() - self._last_regime_time < self.cache_duration:
                print("Using cached regime data")
                return self._last_regime.copy()  # Return a copy to prevent mutations

        # Get Fear & Greed (with its own caching)
        fg_data = self._get_fear_greed_cached(force_refresh)

        # Get VIX for confirmation
        vix = self._get_vix()

        # Interpret into trading regime
        regime = self._interpret_regime(fg_data["value"], vix)

        # Add metadata
        regime.update(
            {
                "fear_greed_value": int(fg_data["value"]),  # Round for display
                "fear_greed_text": fg_data.get("text", ""),
                "vix": round(vix, 2),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Cache the complete regime
        self._last_regime = regime
        self._last_regime_time = time.time()

        return regime

    def _get_fear_greed_cached(self, force_refresh: bool = False) -> Dict:
        """
        Fetch CNN Fear & Greed with caching
        
        Args:
            force_refresh: If True, bypass cache
        """
        cache_key = "fear_greed"

        # Check cache (unless forced refresh)
        if not force_refresh and cache_key in self.cache:
            cached_time = self.cache[cache_key]["timestamp"]
            if time.time() - cached_time < self.cache_duration:
                print(f"Using cached Fear & Greed data")
                return self.cache[cache_key]["data"]

        # Fetch fresh
        try:
            print("Fetching fresh CNN Fear & Greed...")
            data = self.cnn_client.get_fear_and_greed_index()
            
            print(f"Successfully fetched CNN F&G: {data.get('value', 'Unknown')}")

            # Cache it
            self.cache[cache_key] = {"data": data, "timestamp": time.time()}

            return data

        except Exception as e:
            print(f"Error fetching CNN Fear & Greed: {e}")
            
            # Try to use stale cache if available
            if cache_key in self.cache:
                print("Using stale cached data due to fetch error")
                return self.cache[cache_key]["data"]
            
            print("Falling back to VIX-based regime")
            return self._vix_fallback_regime()

    def _get_vix(self) -> float:
        """
        Get current VIX level with caching
        """
        cache_key = "vix"
        
        # Check cache
        if cache_key in self.cache:
            cached_time = self.cache[cache_key]["timestamp"]
            if time.time() - cached_time < self.cache_duration:
                return self.cache[cache_key]["value"]
        
        try:
            vix = yf.Ticker("^VIX")
            value = vix.info["regularMarketPrice"]
            
            # Cache it
            self.cache[cache_key] = {"value": value, "timestamp": time.time()}
            return value
        except:
            return 20.0  # Default to normal if unavailable

    def _vix_fallback_regime(self) -> Dict:
        """
        Fallback regime detection using only VIX
        """
        vix = self._get_vix()

        if vix < 15:
            return {"value": 65, "text": "Greed"}
        elif vix < 20:
            return {"value": 50, "text": "Neutral"}
        elif vix < 30:
            return {"value": 35, "text": "Fear"}
        else:
            return {"value": 15, "text": "Extreme Fear"}

    def _interpret_regime(self, fear_greed_value: float, vix: float) -> Dict:
        """
        Convert Fear & Greed + VIX into trading regime
        Based on your research findings
        """
        # Determine base regime from Fear & Greed
        regime_name = None
        for regime, (min_val, max_val) in REGIME_THRESHOLDS.items():
            if min_val <= fear_greed_value < max_val:
                regime_name = regime
                break

        if not regime_name:
            regime_name = "neutral"

        # Build regime dict
        regime_dict = {
            "regime": regime_name,
            "position_multiplier": POSITION_MULTIPLIERS[regime_name],
            "filter_percentile": FILTER_PERCENTILES[regime_name],
            "expected_win_rate": EXPECTED_WIN_RATES[regime_name],
        }

        # Determine strategy
        if regime_name in ["extreme_fear", "fear"]:
            regime_dict["strategy"] = "mean_reversion"
        elif regime_name in ["greed", "extreme_greed"]:
            regime_dict["strategy"] = "momentum"
        else:
            regime_dict["strategy"] = "mixed"

        # VIX override for extreme conditions
        if vix > 30:
            regime_dict["strategy"] = "mean_reversion"
            regime_dict["expected_win_rate"] = max(
                0.80, regime_dict["expected_win_rate"]
            )
            regime_dict["volatility_regime"] = "high"
        elif vix < 15:
            regime_dict["volatility_regime"] = "low"
        else:
            regime_dict["volatility_regime"] = "normal"

        return regime_dict

    def clear_cache(self):
        """
        Clear all cached data - useful for testing or forcing refresh
        """
        self.cache = {}
        self._last_regime = None
        self._last_regime_time = 0
        print("Regime detector cache cleared")