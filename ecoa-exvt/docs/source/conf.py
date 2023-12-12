# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "EXVT"
copyright = "2023, Dassault Aviation"
author = "Dassault Aviation"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = []
smartquotes = False

# Added HTML balises
# br: insert a new break line
# underline: to underline words
rst_prolog = """
.. |br| raw:: html

    <br />

.. role:: underline
    :class: underline
"""

latex_engine = "xelatex"

# Setting up the package directory

sys.path.insert(0, os.path.abspath(os.path.join("..", "..", "src")))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
