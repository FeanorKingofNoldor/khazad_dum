#!/bin/bash
# KHAZAD_DUM Monitor Startup Script

cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f ".env" ] && [ -f ".env.template" ]; then
    echo "Creating .env from template..."
    cp .env.template .env
    echo "Please edit .env with your database credentials if you want to use real data."
    echo "Otherwise, the monitor will use mock data."
    echo ""
fi

# Check for required packages
echo "Checking dependencies..."
python3 -c "import rich" 2>/dev/null || {
    echo "Installing Rich..."
    pip install rich --break-system-packages --quiet
}

python3 -c "import plotext" 2>/dev/null || {
    echo "Installing Plotext..."
    pip install plotext --break-system-packages --quiet
}

python3 -c "import dotenv" 2>/dev/null || {
    echo "Installing python-dotenv..."
    pip install python-dotenv --break-system-packages --quiet
}

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║   KHAZAD_DUM Position Monitor        ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Select version:"
echo "1) Simple Monitor (menu-driven)"
echo "2) Advanced Monitor (live updates)"
echo "3) Run tests"
echo "4) Exit"
echo ""
read -p "Choice [1-4]: " choice

case $choice in
    1)
        python3 simple_monitor.py
        ;;
    2)
        python3 monitor_cli.py
        ;;
    3)
        python3 test_monitor.py
        ;;
    4)
        echo "Goodbye!"
        ;;
    *)
        echo "Invalid choice. Running simple monitor..."
        python3 simple_monitor.py
        ;;
esac
