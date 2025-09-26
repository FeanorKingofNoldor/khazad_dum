"""
KHAZAD_DUM Monitor Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'khazad_dum'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Display Configuration
REFRESH_RATE = 30  # seconds (0 for manual only)
CHART_HEIGHT = 20  # lines
CHART_WIDTH = 80   # characters

# Colors (plotext color names)
COLORS = {
    'price_line': 'blue',
    'stop_loss': 'red',
    'target': 'green',
    'current': 'yellow',
    'portfolio': 'cyan'
}

# Mock mode for testing without database
USE_MOCK_DATA = os.getenv('USE_MOCK', 'False').lower() == 'true'

# Historical data points to show
HISTORY_DAYS = 30  # Show last 30 days of price data
