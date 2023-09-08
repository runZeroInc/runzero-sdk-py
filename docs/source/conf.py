# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../.."))

import runzero

# -- Project information -----------------------------------------------------

project = "runZero Python SDK"
copyright = f"{datetime.now().year}, runZero, Inc"
author = "runZero, Inc"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "autoapi.extension",
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]


intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autoapi_type = "python"
autoapi_dirs= ["../../runzero"]
autoapi_add_toctree_entry = False
autoapi_options = [
    "members",
    "inherited-members",
    "show-inheritance",
    "show-module-summary",
]
autoapi_template_dir = ""
autoapi_file_patterns = [
    "*.py",
    "*.pyi",
]

autoapi_add_toctree_entry = False
autoapi_python_class_content = "both"
autoapi_member_order = "alphabetical"
autodoc_typehints = "both"
autodoc_typehints_format = "short"
autodoc_typehints_description_target = "documented_params"
autoapi_python_use_implicit_namespaces = False
autoapi_prepare_jinja_env = None
autoapi_keep_files = False
suppress_warnings = []  # type: ignore

linkcheck_ignore = [r'https:\/\/runzero\.local']

# -- Options for View-Code -------------------------------------------------
viewcode_follow_imported_members = True

pygments_style = "default"
smartquotes = True

templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', '_templates']

release = runzero.__version__

# --- HTML output ---
html_title = project + ' v' + release
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#008099",
        "color-brand-content": "#008099",
    },
    "dark_css_variables": {
        "color-brand-primary": "#9ca0a5",
        "color-brand-content": "#9ca0a5",
    },
    "source_repository": "https://github.com/runZeroInc/runzero-sdk-py",
    "source_branch": "main",
    "source_directory": "docs",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/runZeroInc/runzero-sdk-py",
            "class": "",
        },
    ],
    "navigation_with_keys": True,
    "sidebar_hide_name": False,
}

html_theme_options = {
    "light_logo": "img/runZerologo.png",
    "dark_logo": "img/runZerologoDarkmode.png",
}
html_favicon = '_static/img/favicon.ico'
html_css_files = [
    "css/custom.css",
]
html_js_files = [
    "js/custom.js",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

