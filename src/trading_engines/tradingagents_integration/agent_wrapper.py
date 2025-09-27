"""
Agent Wrapper - Interface to TradingAgents
This module provides the main wrapper for TradingAgents integration
"""

# Import the actual AgentWrapper from agent_coordinator
from .agent_coordinator import AgentWrapper

# Export it
__all__ = ['AgentWrapper']
