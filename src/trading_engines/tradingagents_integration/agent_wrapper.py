"""
Agent Wrapper - Interface to TradingAgents
This module provides the main wrapper for TradingAgents integration
"""

# The wrapper functionality is in agent_coordinator for now
from .agent_coordinator import *

# Create alias for backward compatibility
AgentWrapper = Khazad_DumTradingAgentsCoordinator if 'Khazad_DumTradingAgentsCoordinator' in dir() else None
