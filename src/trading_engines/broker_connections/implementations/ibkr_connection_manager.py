#!/usr/bin/env python3
"""
🏔️ KHAZAD_DUM - IBKR Connection Manager
Single entry point for all Interactive Brokers operations

This module provides a centralized connection manager that all IBKR operations
go through, eliminating client ID conflicts and connection duplication.
"""

import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

try:
    from ib_async import IB, Stock, util
    IB_AVAILABLE = True
except ImportError:
    print("Warning: ib_async not installed. Install with: pip install ib_async")
    IB_AVAILABLE = False

logger = logging.getLogger(__name__)


class IBKRConnectionManager:
    """
    Centralized IBKR connection manager implementing singleton pattern
    All IBKR operations should go through this manager
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern - only one instance per process"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(IBKRConnectionManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, host='127.0.0.1', port=4002, client_id=1):
        """Initialize the connection manager (only once due to singleton)"""
        if self._initialized:
            return
            
        if not IB_AVAILABLE:
            raise ImportError("ib_async library not available. Install with: pip install ib_async")
        
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        self._connection_lock = threading.Lock()
        self._cache = {}
        self._cache_timeout = 60  # 60 seconds
        self._last_update = {}
        self._initialized = True
        
        # Connection metadata
        self.connection_type = "LIVE" if port == 4001 else "PAPER"
        
        logger.info(f"IBKR Connection Manager initialized for {self.connection_type} trading")
    
    async def connect(self) -> bool:
        """Establish connection to IBKR"""
        if self.connected:
            logger.debug("Already connected to IBKR")
            return True
        
        try:
            with self._connection_lock:
                if self.connected:  # Double-check after acquiring lock
                    return True
                
                logger.info(f"Connecting to IBKR {self.connection_type} on {self.host}:{self.port} (client {self.client_id})")
                await self.ib.connectAsync(self.host, self.port, self.client_id)
                self.connected = True
                
                logger.info(f"✅ Connected to IBKR ({self.connection_type})")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to IBKR: {e}")
            self.connected = False
            return False
    
    def connect_sync(self) -> bool:
        """Synchronous wrapper for connect"""
        try:
            # Handle event loop properly
            try:
                loop = asyncio.get_running_loop()
                # We're in a loop, use ThreadPoolExecutor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: asyncio.run(self.connect()))
                    return future.result(timeout=30)
            except RuntimeError:
                # No event loop running
                return asyncio.get_event_loop().run_until_complete(self.connect())
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from IBKR"""
        if not self.connected:
            return
        
        try:
            with self._connection_lock:
                if self.connected:
                    self.ib.disconnect()
                    self.connected = False
                    logger.info("✅ Disconnected from IBKR")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def disconnect_sync(self):
        """Synchronous wrapper for disconnect"""
        try:
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: asyncio.run(self.disconnect()))
                    future.result(timeout=10)
            except RuntimeError:
                asyncio.get_event_loop().run_until_complete(self.disconnect())
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    @contextmanager
    def ensure_connection(self):
        """Context manager to ensure connection is active"""
        if not self.connected:
            if not self.connect_sync():
                raise ConnectionError("Failed to establish IBKR connection")
        
        try:
            yield self.ib
        except Exception as e:
            logger.error(f"Error during IBKR operation: {e}")
            raise
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._last_update:
            return False
        
        elapsed = (datetime.now() - self._last_update[cache_key]).total_seconds()
        return elapsed < self._cache_timeout
    
    def get_cache(self, cache_key: str, default=None):
        """Get cached data if valid"""
        if self.is_cache_valid(cache_key):
            return self._cache.get(cache_key, default)
        return default
    
    def set_cache(self, cache_key: str, data: Any):
        """Set cached data with timestamp"""
        self._cache[cache_key] = data
        self._last_update[cache_key] = datetime.now()
    
    def clear_cache(self, cache_key: str = None):
        """Clear cached data"""
        if cache_key:
            self._cache.pop(cache_key, None)
            self._last_update.pop(cache_key, None)
        else:
            self._cache.clear()
            self._last_update.clear()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection status and info"""
        return {
            'connected': self.connected,
            'connection_type': self.connection_type,
            'host': self.host,
            'port': self.port,
            'client_id': self.client_id,
            'cache_items': len(self._cache),
            'last_cache_update': max(self._last_update.values()) if self._last_update else None
        }
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'connected') and self.connected:
            try:
                self.disconnect_sync()
            except:
                pass


# Global instance for easy access
_connection_manager = None

def get_connection_manager(host='127.0.0.1', port=4002, client_id=1) -> IBKRConnectionManager:
    """
    Get the global IBKR connection manager instance
    
    Args:
        host: IBKR host (default: localhost)
        port: IBKR port (4001=live, 4002=paper)
        client_id: Unique client ID (1-32)
    
    Returns:
        IBKRConnectionManager: Singleton connection manager instance
    """
    global _connection_manager
    
    if _connection_manager is None:
        _connection_manager = IBKRConnectionManager(host, port, client_id)
    
    return _connection_manager


def reset_connection_manager():
    """Reset the global connection manager (useful for tests)"""
    global _connection_manager
    if _connection_manager and _connection_manager.connected:
        _connection_manager.disconnect_sync()
    _connection_manager = None


# Convenience functions for common operations
def with_ibkr_connection(func):
    """Decorator to ensure IBKR connection is active"""
    def wrapper(*args, **kwargs):
        manager = get_connection_manager()
        with manager.ensure_connection():
            return func(manager.ib, *args, **kwargs)
    return wrapper


# Example usage and testing
if __name__ == "__main__":
    # Test the connection manager
    import sys
    
    def test_connection_manager():
        """Test the IBKR connection manager"""
        print("Testing IBKR Connection Manager...")
        
        # Get manager instance
        manager = get_connection_manager()
        print(f"Manager created: {manager.get_connection_info()}")
        
        # Test connection
        if manager.connect_sync():
            print("✅ Connection successful!")
            print(f"Connection info: {manager.get_connection_info()}")
            
            # Test context manager
            try:
                with manager.ensure_connection() as ib:
                    print(f"IB instance: {ib}")
                    print("✅ Context manager working")
            except Exception as e:
                print(f"❌ Context manager error: {e}")
            
            # Disconnect
            manager.disconnect_sync()
            print("✅ Disconnected successfully")
            
        else:
            print("❌ Connection failed")
            return False
        
        # Test singleton behavior
        manager2 = get_connection_manager()
        if manager is manager2:
            print("✅ Singleton pattern working")
        else:
            print("❌ Singleton pattern broken")
            
        return True
    
    if test_connection_manager():
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)