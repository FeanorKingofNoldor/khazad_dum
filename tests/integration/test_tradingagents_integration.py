from src.trading_engines.tradingagents_integration.agent_wrapper import AgentWrapper
from dotenv import load_dotenv

load_dotenv()

# Test with one stock
wrapper = AgentWrapper()
result = wrapper.analyze_stock("AAPL")

print(f"Analysis complete:")
print(f"Decision: {result['decision']}")