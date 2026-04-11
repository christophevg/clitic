# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add project source to path
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "clitic"
copyright = "2026, Christophe VG"
author = "Christophe VG"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  "sphinx.ext.autodoc",
  "sphinx.ext.autosummary",
  "sphinx.ext.napoleon",
  "sphinx.ext.viewcode",
  "sphinx.ext.intersphinx",
  "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_member_order = "bysource"
autodoc_default_options = {
  "members": True,
  "undoc-members": True,
  "show-inheritance": True,
}

# -- Options for Napoleon ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# -- Options for Intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
  "python": ("https://docs.python.org/3", None),
  "textual": ("https://textual.textualize.io/", None),
  "rich": ("https://rich.readthedocs.io/en/stable/", None),
}

# -- Options for MyST --------------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/sphinx/introduction.html

myst_enable_extensions = ["colon_fence", "deflist", "html_admonition"]