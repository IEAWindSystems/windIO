import os
import sys
sys.path.insert(0, os.path.abspath("../windIO"))


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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'windIO'
copyright = '2025, IEA Wind Task 55 REFWIND'
author = 'IEA Wind Task 55 REFWIND'

# The full version, including alpha/beta/rc tags
release = 'v1.1'


# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "sphinx_multiversion",
]

napoleon_google_docstring = True
napoleon_use_param = False
napoleon_use_rtype = False

# Add any paths that contain templates here, relative to this directory.
templates_path = [
    "_templates",
]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# html_extra_path = ['_static/switcher.json']

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

html_theme_options = {}
html_theme_options["analytics"] = {
    "google_analytics_id": "G-8GPVFR9N4C",
}
html_theme_options = {
   "navbar_start": ["navbar-logo", "version-switcher"]
   # switcher gets set dynamically
}

html_sidebars = {
    "**": []
}

smv_released_pattern = r'^refs/tags/.*$'
smv_branch_whitelist = r'^main$'

def on_config_inited(app, config):
    # This runs after the config is loaded but before the build starts
    version_match = getattr(config, "smv_current_version", "local")
    print("on_config_inited VERSION",version_match) 
    config.html_theme_options["switcher"] = {
        "json_url": "http://localhost:8000/main/_static/switcher.json",
        "version_match": version_match
    }

def setup(app):
    # Connect our custom handler to the config-inited event
    app.connect("config-inited", on_config_inited)
