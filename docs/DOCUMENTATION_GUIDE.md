# KHAZAD_DUM Documentation Generation Guide

> **📚 Complete guide for generating, maintaining, and deploying documentation**

## 🎯 Overview

KHAZAD_DUM uses **Sphinx** to automatically generate professional API documentation from inline docstrings. This guide covers everything from quick generation to advanced customization.

---

## 🚀 Quick Start

### **Option 1: Automated Build Script (Recommended)**

```bash
# Run the automated build script
cd /home/feanor/khazad_dum
./docs/build_docs.sh
```

**What it does:**
- ✅ Creates isolated documentation virtual environment
- ✅ Installs all Sphinx dependencies
- ✅ Attempts to install project dependencies for better autodoc
- ✅ Builds HTML documentation
- ✅ Offers to open in browser
- ✅ Provides local server instructions

### **Option 2: Manual Build**

```bash
cd /home/feanor/khazad_dum

# Activate documentation environment
source .venv-docs/bin/activate

# Build documentation
cd docs/api
PYTHONPATH="/home/feanor/khazad_dum:$PYTHONPATH" sphinx-build -b html . _build
```

### **Option 3: Live Server for Development**

```bash
# After building, serve locally
cd docs/api/_build
python -m http.server 8000

# Open: http://localhost:8000
```

---

## 📁 Documentation Structure

```
docs/
├── build_docs.sh                    # Automated build script
├── DOCUMENTATION_GUIDE.md           # This guide
├── DOCUMENTATION_STANDARDS.md       # Coding standards and templates
├── api/                             # Sphinx documentation
│   ├── conf.py                      # Sphinx configuration
│   ├── index.rst                    # Main documentation index
│   └── _build/                      # Generated HTML (after build)
├── guides/                          # User guides
│   ├── DOCKER_GUIDE.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── QUICK_REFERENCE.md
└── README.md                        # Documentation index
```

---

## 🔧 Customizing Documentation

### **Sphinx Configuration (`docs/api/conf.py`)**

Key settings you can modify:

```python
# Project information
project = 'KHAZAD_DUM'
author = 'FeanorKingofNoldor'
release = '1.0.0'

# Theme settings
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'collapse_navigation': False,
    'navigation_depth': 4,
}

# Extensions for better documentation
extensions = [
    'sphinx.ext.autodoc',        # Auto-generate from docstrings
    'sphinx.ext.autosummary',    # Generate summary tables
    'sphinx.ext.napoleon',       # Google/NumPy style docstrings
    'sphinx.ext.intersphinx',    # Link to other documentation
    'sphinx.ext.todo',           # TODO directives
]
```

### **Adding New Modules to Documentation**

1. **Add to the main index** (`docs/api/index.rst`):

```rst
.. automodule:: src.new_module.new_component
   :members:
   :undoc-members:
   :show-inheritance:
```

2. **Create dedicated module documentation**:

```rst
New Module
==========

.. automodule:: src.new_module.new_component
   :members:
   :special-members:
   :private-members:
```

### **Theme Customization**

Create `docs/api/_static/custom.css`:

```css
/* KHAZAD_DUM custom styling */
.wy-side-nav-search {
    background-color: #2c3e50;
}

.wy-side-nav-search .wy-dropdown > a {
    color: #ecf0f1;
    font-weight: bold;
}

/* ASCII art styling */
pre.literal-block {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.2;
}
```

Then add to `conf.py`:
```python
html_static_path = ['_static']
html_css_files = ['custom.css']
```

---

## 📖 Docstring Best Practices

### **Google Style Docstrings** (Preferred)

```python
def analyze_market_regime(self, data: pd.DataFrame, 
                         confidence: float = 0.8) -> Dict[str, Any]:
    """
    Analyze current market regime using multiple indicators.
    
    This function combines CNN Fear & Greed Index with VIX data to classify
    the current market environment. The classification drives position sizing
    and risk management throughout the trading pipeline.
    
    Args:
        data (pd.DataFrame): Market data containing OHLCV information.
            Must include columns: ['Open', 'High', 'Low', 'Close', 'Volume']
        confidence (float, optional): Minimum confidence threshold for regime
            classification. Must be between 0.0 and 1.0. Defaults to 0.8.
            
    Returns:
        Dict[str, Any]: Regime analysis containing:
            - 'regime': str, one of ['extreme_fear', 'fear', 'neutral', 'greed', 'extreme_greed']
            - 'confidence': float, confidence score (0.0 to 1.0)
            - 'fear_greed_index': int, CNN F&G Index value (0-100)
            - 'vix_level': float, current VIX level
            - 'recommended_position_size': float, position multiplier
            
    Raises:
        ValueError: If confidence is not between 0.0 and 1.0
        DataError: If required columns are missing from data
        ConnectionError: If unable to fetch Fear & Greed data
        
    Example:
        >>> detector = RegimeDetector()
        >>> market_data = fetch_market_data(['SPY'])
        >>> regime = detector.analyze_market_regime(market_data, confidence=0.75)
        >>> print(f"Current regime: {regime['regime']}")
        Current regime: fear
        
        >>> if regime['confidence'] > 0.8:
        ...     position_size = regime['recommended_position_size']
        ...     print(f"Recommended position multiplier: {position_size}x")
        Recommended position multiplier: 1.3x
        
    Note:
        This method caches results for 300 seconds to minimize API calls.
        For real-time analysis, use force_refresh=True parameter.
        
    Performance:
        - Typical execution time: 200-500ms (network dependent)
        - Memory usage: ~2MB for standard S&P 500 dataset
        - API calls: 2 per execution (CNN F&G + VIX)
        
    See Also:
        get_vix_data(): Fetch current VIX levels
        get_fear_greed_index(): Get CNN Fear & Greed Index
        calculate_position_multiplier(): Calculate position sizing
    """
```

### **Module-Level Docstrings**

```python
#!/usr/bin/env python3
"""
Market regime detection and classification system.

This module implements the first stage of the KHAZAD_DUM trading pipeline,
analyzing market sentiment and volatility to classify trading conditions.
The regime classification influences all downstream trading decisions.

Classes:
    RegimeDetector: Main class for regime detection and analysis
    RegimeHistory: Historical regime tracking and analysis
    
Functions:
    get_current_market_state(): Quick regime check without caching
    validate_regime_thresholds(): Validate configuration parameters
    
Constants:
    REGIME_THRESHOLDS (Dict[str, Tuple[int, int]]): F&G Index thresholds
    DEFAULT_CACHE_DURATION (int): Default cache duration in seconds
    
Example:
    Basic usage:
    
    >>> from src.core.market_analysis.regime_detector import RegimeDetector
    >>> detector = RegimeDetector()
    >>> current_regime = detector.get_current_regime()
    >>> print(f"Market regime: {current_regime['regime']}")
    
    Advanced usage with custom configuration:
    
    >>> config = {
    ...     'cache_duration': 600,
    ...     'fallback_enabled': True,
    ...     'vix_override': True
    ... }
    >>> detector = RegimeDetector(config=config)
    >>> regime = detector.analyze_market_regime(data, confidence=0.85)

Note:
    This module requires active internet connection for CNN Fear & Greed Index.
    VIX data fallback is available when primary feeds are unavailable.
    
Warning:
    Regime classification is a simplification of complex market dynamics.
    Always combine with additional analysis for trading decisions.
"""
```

---

## 🔄 Continuous Documentation

### **Pre-Commit Documentation Checks**

Create `.pre-commit-hooks.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-docstrings
        name: Check Python Docstrings
        entry: python -c "import ast, sys; [exit(1) for f in sys.argv[1:] if not ast.parse(open(f).read()).body[0].value or not isinstance(ast.parse(open(f).read()).body[0].value.s, str)]"
        language: system
        files: \\.py$
      
      - id: build-docs
        name: Build Documentation
        entry: ./docs/build_docs.sh
        language: system
        pass_filenames: false
        stages: [manual]
```

### **GitHub Actions for Documentation**

Create `.github/workflows/docs.yml`:

```yaml
name: Build Documentation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install sphinx sphinx-rtd-theme sphinxcontrib-napoleon
        
    - name: Build documentation
      run: |
        cd docs/api
        sphinx-build -b html -W -E . _build
        
    - name: Upload documentation
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: docs/api/_build/
```

---

## 🚀 Deployment Options

### **GitHub Pages Deployment**

1. **Enable GitHub Pages** in repository settings
2. **Add deployment workflow** (`.github/workflows/pages.yml`):

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install Sphinx
      run: |
        pip install sphinx sphinx-rtd-theme sphinxcontrib-napoleon
        
    - name: Build docs
      run: |
        cd docs/api
        sphinx-build -b html . _build
        
    - name: Setup Pages
      uses: actions/configure-pages@v3
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: docs/api/_build
        
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
```

### **Local Documentation Server**

```bash
# Development server with auto-reload
cd docs/api
sphinx-autobuild . _build --port 8000

# Production-like server
cd docs/api/_build
python -m http.server 8080 --bind 0.0.0.0
```

---

## 🛠️ Troubleshooting

### **Common Issues**

**1. "Module not found" errors during build**
```bash
# Install missing dependencies
source .venv-docs/bin/activate
pip install pandas yfinance requests beautifulsoup4

# Or use mock imports in conf.py
autodoc_mock_imports = ['pandas', 'yfinance', 'requests']
```

**2. "No module named 'src'"**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="/home/feanor/khazad_dum:$PYTHONPATH"

# Or add to conf.py
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
```

**3. Docstring formatting warnings**
- Check Google-style docstring syntax
- Ensure proper indentation
- Validate RST syntax in docstrings

**4. Theme issues**
```bash
# Reinstall theme
pip install --force-reinstall sphinx-rtd-theme
```

### **Debug Mode**

```bash
# Build with verbose output
sphinx-build -b html -v -W . _build

# Build with error details
sphinx-build -b html -E -a . _build
```

---

## 📊 Documentation Metrics

### **Coverage Analysis**

```bash
# Check docstring coverage
pip install docstr-coverage
docstr-coverage src/

# Generate coverage report
docstr-coverage --html-report src/
```

### **Quality Metrics**

Track these metrics for documentation health:

- **Docstring coverage**: % of functions with docstrings
- **Example coverage**: % of public functions with examples
- **Type annotation coverage**: % of functions with type hints
- **Build warnings**: Number of Sphinx warnings
- **Dead links**: Broken internal/external references

---

## 🎨 Advanced Features

### **Interactive Documentation**

```python
# Add interactive examples with Jupyter notebooks
extensions.append('nbsphinx')

# Include executable code blocks
extensions.append('sphinx.ext.doctest')
```

### **API Reference Automation**

```bash
# Auto-generate module documentation
sphinx-apidoc -o docs/api/generated src/
```

### **Cross-References**

```python
def related_function():
    """
    Related function documentation.
    
    See Also:
        :func:`analyze_market_regime`: Main regime analysis
        :class:`RegimeDetector`: Core regime detection class
        :mod:`src.core.market_analysis`: Full module documentation
    """
```

---

## ✅ Documentation Checklist

Before committing documentation changes:

### **Content**
- [ ] All public functions have docstrings
- [ ] All classes have docstrings with examples
- [ ] Module-level docstrings are comprehensive
- [ ] Examples can be executed
- [ ] Type annotations are complete

### **Structure**
- [ ] New modules added to index.rst
- [ ] TOC structure is logical
- [ ] Cross-references are working
- [ ] External links are valid

### **Quality**
- [ ] Sphinx build succeeds without errors
- [ ] No broken internal references
- [ ] HTML output looks professional
- [ ] Mobile-friendly formatting
- [ ] Search functionality works

### **Automation**
- [ ] Build script works
- [ ] Documentation builds in CI/CD
- [ ] Deployment pipeline functions
- [ ] Version updates are automated

---

*🎯 **Remember**: Great documentation is living documentation—it evolves with your code and serves your users' needs!*

## 📞 Need Help?

- **Sphinx Documentation**: https://www.sphinx-doc.org/
- **Read the Docs Theme**: https://sphinx-rtd-theme.readthedocs.io/
- **Google Style Guide**: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings