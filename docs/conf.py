#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime

this_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(this_directory, ".."))

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",  # google style docstrings
    "sphinx_autodoc_typehints",  # must be after napoleon
]


templates_path = []
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "monitorcontrol"
year = datetime.datetime.now().year
author = "Alex M."
copyright = f"{year}, {author}"
version = "1.6"
release = "1.6"
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".tox"]
pygments_style = "sphinx"
todo_include_todos = True
nitpicky = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# HTML Options

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "monitorcontroldoc"
html_theme_options = {"display_version": False}
html_context = {
    "display_github": True,
    "github_user": "newAM",
    "github_repo": project,
}
