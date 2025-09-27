.. KHAZAD_DUM documentation master file

=====================================
KHAZAD_DÛM API Documentation
=====================================

.. raw:: html

   <div style="text-align: center; padding: 20px;">
   <h1 style="font-family: monospace; color: #2c3e50;">
   ███████╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗<br>
   ██╔════╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║<br>
   ██║     ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║<br>
   ██║     ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║<br>
   ╚██████╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║<br>
    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝<br>
   </h1>
   <h3 style="color: #34495e; font-style: italic;">
   🏔️ Algorithmic Trading System - "They delved too greedily and too deep..."
   </h3>
   </div>

.. centered:: **Created by FeanorKingofNoldor** | `GitHub Repository <https://github.com/FeanorKingofNoldor/khazad_dum>`_

Welcome to the KHAZAD_DÛM API Documentation! This documentation is automatically generated from the codebase docstrings and provides comprehensive information about all classes, functions, and modules in the algorithmic trading system.

========
Overview
========

KHAZAD_DÛM is a sophisticated algorithmic trading system that implements a 6-stage pipeline:

1. **Market Regime Detection** - Classify market conditions using sentiment indicators
2. **Stock Screening** - Multi-layer filtering from S&P 500 universe
3. **AI Analysis** - TradingAgents framework for fundamental/technical research
4. **Pattern Recognition** - Historical pattern learning with memory injection
5. **Portfolio Construction** - Regime-aware position sizing and risk management
6. **Performance Observation** - Continuous feedback loops for system improvement

=================
System Architecture
=================

.. toctree::
   :maxdepth: 2
   :caption: Core Components

   core/market_analysis
   core/stock_screening
   core/pattern_recognition
   core/portfolio_management

.. toctree::
   :maxdepth: 2
   :caption: Data Pipeline

   data_pipeline/market_data
   data_pipeline/storage
   data_pipeline/external_apis

.. toctree::
   :maxdepth: 2
   :caption: Trading Engines

   trading_engines/tradingagents_integration
   trading_engines/broker_connections

.. toctree::
   :maxdepth: 2
   :caption: Configuration & Utilities

   config
   utils

================
Quick Start Guide
================

For developers new to the codebase:

1. **Read the main README**: Start with the project overview
2. **Check the Quick Reference**: ``docs/reference/QUICK_REFERENCE.md`` for immediate setup
3. **Explore this API documentation**: Navigate through the modules below
4. **Run the examples**: Each module includes executable examples in docstrings

===================
API Reference
===================

.. autosummary::
   :toctree: generated
   :template: module.rst
   :recursive:

   src.core
   src.data_pipeline
   src.trading_engines
   src.integrations

===================
Module Details
===================

Core Modules
------------

.. automodule:: src.core
   :members:
   :undoc-members:
   :show-inheritance:

Market Analysis
~~~~~~~~~~~~~~~

.. automodule:: src.core.market_analysis.regime_detector
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.core.market_analysis.cnn_feed_parser
   :members:
   :undoc-members:
   :show-inheritance:

Stock Screening
~~~~~~~~~~~~~~~

.. automodule:: src.core.stock_screening.stock_filter
   :members:
   :undoc-members:
   :show-inheritance:

Pattern Recognition
~~~~~~~~~~~~~~~~~~~

.. automodule:: src.core.pattern_recognition.pattern_classifier
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.core.pattern_recognition.pattern_tracker
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.core.pattern_recognition.memory_injector
   :members:
   :undoc-members:
   :show-inheritance:

Portfolio Management
~~~~~~~~~~~~~~~~~~~~

.. automodule:: src.core.portfolio_management.portfolio_constructor
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.core.portfolio_management.position_tracker
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.core.portfolio_management.performance_observer
   :members:
   :undoc-members:
   :show-inheritance:

Data Pipeline
-------------

Storage
~~~~~~~

.. automodule:: src.data_pipeline.storage.database_manager
   :members:
   :undoc-members:
   :show-inheritance:

Market Data
~~~~~~~~~~~

.. automodule:: src.data_pipeline.market_data
   :members:
   :undoc-members:
   :show-inheritance:

Trading Engines
---------------

TradingAgents Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: src.trading_engines.tradingagents_integration.batch_processor
   :members:
   :undoc-members:
   :show-inheritance:

===================
Configuration
===================

.. automodule:: config.settings.base_config
   :members:
   :undoc-members:

===================
Development Guide
===================

Adding Documentation
--------------------

All Python files in KHAZAD_DÛM should follow these documentation standards:

1. **File Headers**: Use the template from ``docs/templates/file_header_template.py``
2. **Docstrings**: Follow Google-style docstrings for all classes and functions
3. **Type Hints**: Use comprehensive type annotations
4. **Examples**: Include usage examples in docstrings

Example Function Documentation::

    def process_symbols(symbols: List[str], 
                       config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a list of stock symbols through the trading pipeline.
        
        Args:
            symbols (List[str]): Stock symbols to process (e.g., ['AAPL', 'MSFT'])
            config (Dict[str, Any], optional): Custom configuration. Defaults to None.
            
        Returns:
            Dict[str, Any]: Processing results with metadata
            
        Raises:
            ValueError: If symbols list is empty
            
        Example:
            >>> results = process_symbols(['AAPL', 'MSFT'])
            >>> print(len(results['processed']))
            2
        """

Building Documentation
----------------------

To build the HTML documentation::

    cd docs/api
    sphinx-build -b html . _build

The generated documentation will be available in ``docs/api/_build/index.html``.

===================
Indices and Tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

===================
Contact & Links
===================

- **Author**: FeanorKingofNoldor
- **Repository**: https://github.com/FeanorKingofNoldor/khazad_dum
- **Documentation**: Generated automatically from docstrings
- **License**: MIT License

.. note::
   This documentation is automatically generated from the source code docstrings.
   For the most up-to-date information, always refer to the source code itself.

.. warning::
   KHAZAD_DÛM is a trading system that involves financial risk. Always thoroughly
   test any modifications in a paper trading environment before deploying to live markets.

---

*"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare to delve deep enough..."*