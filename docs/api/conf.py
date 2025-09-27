# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options. For a full
# list see the documentation: https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../src/'))

# -- Project information -----------------------------------------------------
project = 'KHAZAD_DUM'
copyright = '2024, FeanorKingofNoldor'
author = 'FeanorKingofNoldor'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',         # Include documentation from docstrings
    'sphinx.ext.autosummary',     # Generate summary tables for modules/classes
    'sphinx.ext.viewcode',        # Include source code in documentation
    'sphinx.ext.napoleon',        # Support for Google and NumPy docstrings
    'sphinx.ext.intersphinx',     # Link to external documentation
    'sphinx.ext.githubpages',     # Publish HTML docs in GitHub Pages
    'sphinx.ext.todo',            # Support for todo items
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
html_theme_options = {
    'canonical_url': 'https://github.com/FeanorKingofNoldor/khazad_dum',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2c3e50',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'khazad_dum_custom.css',
]

# The master toctree document.
master_doc = 'index'

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------
# Links to external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# -- Options for autodoc extension -------------------------------------------
# This value selects what content will be inserted into the main body of an autoclass directive
autoclass_content = 'both'  # Include both class docstring and __init__ docstring

# This value is a list of autodoc directive flags that should be automatically applied to all autodoc directives
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']

# This value controls the docstrings inheritance
autodoc_inherit_docstrings = True

# If true, autosummary will generate stub files for the entries listed in autosummary directives
autosummary_generate = True

# -- Options for todo extension ----------------------------------------------
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Custom configuration for KHAZAD_DUM ------------------------------------

# HTML page title
html_title = f"{project} Documentation"

# HTML short title
html_short_title = "KHAZAD_DUM"

# Language for content autogenerated by Sphinx
language = 'en'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_emit_warnings = True

# Custom footer text
html_context = {
    'display_github': True,
    'github_user': 'FeanorKingofNoldor',
    'github_repo': 'khazad_dum',
    'github_version': 'main/docs/api/',
}

# Logo configuration (if you have a logo)
# html_logo = '_static/khazad_dum_logo.png'

# Favicon (if you have one)
# html_favicon = '_static/favicon.ico'