import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "MCP-Workflows"
copyright = "2025, justin"
author = "justin"
release = "0.1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",      # Automatically document modules
    "sphinx.ext.viewcode",     # Add source code links
    "sphinx.ext.napoleon",     # Support for Google/NumPy style docstrings
    "sphinx.ext.coverage",     # Check documentation coverage
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output configuration
html_theme = "alabaster"
html_static_path = ["_static"]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
