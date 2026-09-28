
"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import os
import sys

from typing import Any
from pathlib import Path
from sphinx.locale import _

from sphinx.application import Sphinx

sys.path.append(str(Path(".").resolve()))

# -- Plotly configuration -----------------------------------------------------
import plotly.io as pio
pio.renderers.default = 'sphinx_gallery_png'

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'WaveSongs'
copyright = 'SAN, 2025-present'
author = 'Sebastian Aguilera Novoa'
release = '0.0.7b0'
language = "en"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "myst_nb",
    "myst_parser",
    "sphinx_design",
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    'sphinx.ext.mathjax',
    'sphinxcontrib.bibtex',
    "sphinx_togglebutton",
    'sphinx_gallery.gen_gallery',
    "IPython.sphinxext.ipython_console_highlighting",
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    "autoapi.extension",
    "sphinx.ext.graphviz",
    "sphinx_favicon"
    # "jupyterlite_sphinx",
    # 'sphinx.ext.autosectionlabel',
    # "sphinx.ext.todo",
    # "nbsphinx",
    # "numpydoc",
]

jupyterlite_config = "jupyterlite_config.json"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# intersphinx_mapping = {"wavesongs": ("https://www.wavesongs.github.io", None)}

# -- Sitemap -----------------------------------------------------------------

# # ReadTheDocs has its own way of generating sitemaps, etc.
# if not os.environ.get("READTHEDOCS"):
#     extensions += ["sphinx_sitemap"]

#     html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://127.0.0.1:8000/")
#     sitemap_locales = [None]
#     sitemap_url_scheme = "{link}"

# -- MyST options ------------------------------------------------------------

# This allows us to use ::: to denote directives, useful for admonitions
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]

myst_heading_anchors = 2
myst_substitutions = {"rtd": "[Read the Docs](https://readthedocs.org/)"}
myst_url_schemes = ("http", "https", "mailto")

# MyST-NB settings
# nb_execution_mode = "auto"
# nb_execution_timeout = 100

# -- sphinx_ext_graphviz options ---------------------------------------------

graphviz_output_format = "svg"
inheritance_graph_attrs = dict(
    rankdir="LR",
    fontsize=14,
    ratio="compress",
)

# -- sphinx_togglebutton options ---------------------------------------------
togglebutton_hint = str(_("Click to expand"))
togglebutton_hint_hide = str(_("Click to collapse"))

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_logo = "" # "_static/logo.svg"
html_favicon = "" # "_static/logo.svg"
html_sourcelink_suffix = ""
html_last_updated_fmt = ""  # to reveal the build date in the pages meta

# Define the json_url for our version switcher.
# json_url = "https://pydata-sphinx-theme.readthedocs.io/en/latest/_static/switcher.json"


html_theme_options = {
    "external_links": [
        # {
        #     "url": "https://pydata.org",
        #     "name": "PyData Website",
        # },
    ],
    "header_links_before_dropdown": 5, # 4
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/wavesongs/wavesongs",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/wavesongs",
            "icon": "fa-custom fa-pypi",
        }
    ],
    "logo": {
        "text": "Wavesongs",
        "image_dark": "",
    },
    "use_edit_page_button": True,
    "show_toc_level": 2,
    # [left, content, right] For testing that the navbar items align properly
    "navbar_align": "content",
    "show_nav_level": 2,
    # "announcement": "https://raw.githubusercontent.com/pydata/pydata-sphinx-theme/main/docs/_templates/custom-template.html",
    # "show_version_warning_banner": True,
    "navbar_center": ["navbar-nav"], # "version-switcher", 
    "navbar_start": ["navbar-logo"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # "navbar_persistent": ["search-field"],
    # "primary_sidebar_end": ["custom-template", "sidebar-ethical-ads"],
    # "article_footer_items": ["test", "test"],
    # "content_footer_items": ["test", "test"],
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "secondary_sidebar_items": {
        "auto_examples/*": ["page-toc", "sg_launcher_links", "sg_download_links"],
        "**": ["page-toc", "edit-this-page", "sourcelink"],
    },
    # "switcher": {
    #     "json_url": json_url,
    #     "version_match": version_match,
    # },
    "back_to_top_button": True,
    # "search_as_you_type": True,
}

html_sidebars = {
    "community/index": [
        "sidebar-nav-bs",
        "custom-template",
    ],  # This ensures we test for custom sidebars
    # "examples/no-sidebar": [],  # Test what page looks like with no sidebar items
    # "examples/persistent-search-field": ["search-field"],
    # Blog sidebars
    # ref: https://ablog.readthedocs.io/manual/ablog-configuration-options/#blog-sidebars
    # "examples/blog/*": [
    #     "ablog/postcard.html",
    #     "ablog/recentposts.html",
    #     "ablog/tagcloud.html",
    #     "ablog/categories.html",
    #     "ablog/authors.html",
    #     "ablog/languages.html",
    #     "ablog/locations.html",
    #     "ablog/archives.html",
    # ],
}

html_context = {
    "github_user": "wavesongs",
    "github_repo": "wavesongs",
    "github_version": "main",
    "doc_path": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = [
    # ("custom-icons.js", {"defer": "defer"}),
]
todo_include_todos = True


# -- application setup -------------------------------------------------------

def setup_to_main(
    app: Sphinx, pagename: str, templatename: str, context, doctree
) -> None:
    """
    Add a function that jinja can access for returning an "edit this page" link
    pointing to `main`.
    """

    if pagename.startswith("auto_examples"):
        app.add_css_file("css/hide_links.css")

    def to_main(link: str) -> str:
        """
        Transform "edit on github" links and make sure they always point to the
        main branch.

        Args:
            link: the link to the github edit interface

        Returns:
            the link to the tip of the main branch for the same file
        """
        links = link.split("/")
        idx = links.index("edit")
        return "/".join(links[: idx + 1]) + "/main/" + "/".join(links[idx + 2 :])

    context["to_main"] = to_main

def setup(app: Sphinx) -> dict[str, Any]:
    """Add custom configuration to sphinx app.

    Args:
        app: the Sphinx application
    Returns:
        the 2 parallel parameters set to ``True``.
    """
    app.connect("html-page-context", setup_to_main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

# -- Options for autosummary/autodoc output ------------------------------------
autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "groupwise"

# -- Options for autoapi -------------------------------------------------------
autoapi_type = "python"
autoapi_dirs = ["../wavesongs"]
autoapi_keep_files = True
autoapi_root = "api"
autoapi_member_order = "groupwise"

# -- Options for bibtex -------------------------------------------------------
bibtex_bibfiles = [
    'references/references.bib',
    "references/articles.bib",
    "references/software.bib",
    "references/others.bib"
]
bibtex_default_style = "plain" # unsrt, alpha, plain
# bibtex_encoding = 'latin'

# -- Options for Sphinx-Gallery -----------------------------------------------
examples_dirs = os.path.join('..', 'examples')
gallery_dirs = ['auto_examples']

sphinx_gallery_conf = {
     'examples_dirs': examples_dirs,   # path to your example scripts
     'gallery_dirs': gallery_dirs,  # path to where to save gallery generated output
     'image_scrapers': ("plotly.io._sg_scraper.plotly_sg_scraper"),
     'backreferences_dir': 'gen_modules/backreferences',  # directory where function/class granular galleries are stored
     "promote_jupyter_magic": False,
     'doc_module': ('WaveSongs'),  # Modules for which function/class level galleries are created.
     'reference_url': {'WaveSongs': None,  # The module you locally document uses None
                       'numpy': 'https://docs.scipy.org/doc/numpy/',
                    #    'scipy': 'https://docs.scipy.org/doc/scipy/reference/',
                       'matplotlib': 'https://matplotlib.org/stable'
                   },
    "capture_repr": ("_repr_html_", "__repr__"),
    "matplotlib_animations": True,
    'plot_gallery': True,
    "nested_sections": True,
    "show_api_usage": True,
    'show_memory': True,
    # "reset_modules": ("matplotlib", "seaborn", "sg_doc_build.reset_others"),
    # 'ignore_repr_types': r'matplotlib\.(text|axes)',
     }
