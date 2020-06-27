###############################################################################
# Copyright 2019 Alex M.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

import datetime
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(this_dir, ".."))
from monitorcontrol.__main__ import get_parser  # noqa: E402

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",  # google style docstrings
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

parser = get_parser()
with open(os.path.join(this_dir, "cli.txt"), "w") as f:
    parser.print_help(f)
