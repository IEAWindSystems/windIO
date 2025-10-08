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
release = 'v2.0-alpha'


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
smv_branch_whitelist = r'^(remotes/origin/)?(main)$'
smv_remote_whitelist = r'^(origin)$'

def on_config_inited(app, config):
    # This runs after the config is loaded but before the build starts
    version_match = getattr(config, "smv_current_version", "local")
    DEPLOY_URL = os.environ.get("DEPLOY_URL", "https://ieawindsystems.github.io/windIO")
    print("on_config_inited VERSION", version_match, DEPLOY_URL) 
    config.html_theme_options["switcher"] = {
        "json_url": "%s/main/_static/switcher.json" % DEPLOY_URL,
        "version_match": version_match
    }

def schema_export(app):
    #  This function will be called after a document is processed



    version = getattr(app.config, "smv_current_version")

    # Skip schema export for version 1.0
    if version == "1.0":
        return

    # run the schema_export script in a subprocess, since we otherwise
    # for some reason pick up the windIO/yaml.py file when
    # json_schema_for_humans imports yaml.
    import subprocess
    import os

    env = os.environ.copy()

    subprocess.run(["python", "schema_export.py"], env=env)
    return


    from pathlib import Path

    from json_schema_for_humans.generate import generate_from_filename
    from json_schema_for_humans.generation_configuration import GenerationConfiguration



    # Configure the docs
    config = GenerationConfiguration(
        minify=False,
        copy_css=True,
        copy_js=True,
        expand_buttons=True,
        show_breadcrumbs=False,     # True doesn't seem to work
        show_toc=True,
        collapse_long_descriptions=True,
        collapse_long_examples=True,
        description_is_markdown=True,
        examples_as_yaml=True,
        link_to_reused_ref=True,    # Should we do this or duplicate the entry?
        deprecated_from_description=True,
        template_md_options={
        #     "badge_as_image": True,
            "show_heading_numbers": True
        },
        # template_name="md_nested"
        custom_template_path="jsfh_template/base.html"
    )

    config.schema_title=False

    # Using the json file and config from above, create the docs web page
    base_path = Path(os.getcwd()).parent

    # Generate the plant schema html

    schema_html_path = Path("_static/plant_schema.html")
    generate_from_filename(
        base_path / "windIO" / "schemas" / "plant" / "wind_energy_system.yaml",
        schema_html_path,
        config=config
    )

    # Generate the turbine schema html
    schema_html_path = Path("_static/turbine_schema.html")
    generate_from_filename(
        base_path / "windIO" / "schemas" / "turbine" / "turbine_schema.yaml",
        schema_html_path,
        config=config
    )



def setup(app):
    # Connect our custom handler to the config-inited event
    app.connect("config-inited", on_config_inited)
    app.connect('builder-inited', schema_export)