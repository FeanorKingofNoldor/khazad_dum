#!/bin/bash

# KHAZAD_DUM Documentation Build Script
# Builds API documentation using Sphinx with virtual environment

set -e  # Exit on error

echo "🏔️  KHAZAD_DUM Documentation Builder"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

REPO_ROOT="/home/feanor/khazad_dum"
VENV_PATH="$REPO_ROOT/.venv-docs"
DOCS_PATH="$REPO_ROOT/docs/api"

# Function to print colored status
print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cd "$REPO_ROOT"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    print_status "Creating documentation virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install/upgrade Sphinx and dependencies
print_status "Installing/updating Sphinx dependencies..."
pip install --upgrade pip
pip install sphinx sphinx-rtd-theme sphinxcontrib-napoleon

# Install project dependencies (optional - helps with autodoc)
print_warning "Attempting to install project dependencies for better autodoc..."
pip install pandas yfinance requests beautifulsoup4 || {
    print_warning "Some project dependencies failed to install - docs will have warnings"
}

# Clean previous build
if [ -d "$DOCS_PATH/_build" ]; then
    print_status "Cleaning previous build..."
    rm -rf "$DOCS_PATH/_build"
fi

# Build documentation
print_status "Building Sphinx documentation..."
cd "$DOCS_PATH"
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

# Run Sphinx build with error handling
if sphinx-build -b html . _build; then
    print_success "Documentation built successfully!"
    
    # Check for main index file
    if [ -f "_build/index.html" ]; then
        print_success "Main documentation index created at: $DOCS_PATH/_build/index.html"
        
        # Try to open in browser (optional)
        if command -v xdg-open > /dev/null; then
            read -p "Open documentation in browser? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                xdg-open "$DOCS_PATH/_build/index.html"
            fi
        fi
    else
        print_error "Documentation build failed - index.html not found"
        exit 1
    fi
else
    print_error "Sphinx build failed"
    exit 1
fi

print_success "Documentation build complete!"
print_status "📚 View your docs at: file://$DOCS_PATH/_build/index.html"
print_status "🚀 To serve locally: python -m http.server --directory $DOCS_PATH/_build 8000"

deactivate