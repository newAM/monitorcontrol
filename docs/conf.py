import datetime
import os
import sys
import toml

this_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(this_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from monitorcontrol.__main__ import get_parser  # noqa: E402

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",  # google style docstrings
]

templates_path = []
source_suffix = ".rst"

with open(os.path.join(repo_root, "pyproject.toml"), "r") as f:
    pyproject = toml.load(f)

# The master toctree document.
master_doc = "index"

# General information about the project.
project = pyproject["project"]["name"]
year = datetime.datetime.now().year
author = pyproject["project"]["authors"][0]["name"]
copyright = f"2019 - {year}, {author}"  # noqa: A001
version = pyproject["project"]["version"]
release = pyproject["project"]["version"]
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".tox"]
pygments_style = "sphinx"
todo_include_todos = True
nitpicky = True

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# HTML Options

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = "monitorcontroldoc"
github_user = "newAM"
html_context = {
    "display_github": True,
    "github_user": github_user,
    "github_repo": project,
    # https://github.com/readthedocs/sphinx_rtd_theme/issues/465
    "github_version": "main",
    "conf_py_path": "/docs/",  # needs leading and trailing slashes
}

parser = get_parser()
with open(os.path.join(this_dir, "cli.txt"), "w") as f:
    parser.print_help(f)
