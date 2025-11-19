# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'WaveSongs'
copyright = 'SAN, 2025-present'
author = 'Sebastian Aguilera Novoa'
release = '0.0.3b1'
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
    # 'sphinx.ext.intersphinx',
    # "autoapi.extension",
    # "jupyterlite_sphinx",
    # 'sphinx.ext.autosectionlabel',
    # "sphinx.ext.graphviz",
]

bibtex_bibfiles = [
    'references/references.bib',
    "references/articles.bib",
    "references/software.bib",
    "references/others.bib"
]
bibtex_default_style = 'unsrt'
# bibtex_encoding = 'latin'

# MyST-NB settings
nb_execution_mode = "auto"
nb_execution_timeout = 100

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
myst_url_schemes = ("http", "https", "mailto")
myst_heading_anchors = 2

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


# -- Sphinx-copybutton options ---------------------------------------------
# Exclude copy button from appearing over notebook cell numbers by using :not()
# The default copybutton selector is `div.highlight pre`
# https://github.com/executablebooks/sphinx-copybutton/blob/master/sphinx_copybutton/__init__.py#L82
copybutton_exclude = ".linenos, .gp"
copybutton_selector = ":not(.prompt) > div.highlight pre"







# examples_dirs = ["../examples", "../tutorials"]
# gallery_dirs = ["auto_examples", "tutorials"]
# Set plotly renderer to capture _repr_html_ for sphinx-gallery
# import plotly.io as pio
# pio.renderers.default = "sphinx_gallery_png" # 'sphinx_gallery'

examples_dirs = os.path.join('..', 'examples')
gallery_dirs = ['auto_examples']

sphinx_gallery_conf = {
     'examples_dirs': examples_dirs,   # path to your example scripts
     'gallery_dirs': gallery_dirs,  # path to where to save gallery generated output
    #  'image_scrapers': ("plotly.io._sg_scraper.plotly_sg_scraper"),
     'backreferences_dir': 'gen_modules/backreferences',  # directory where function/class granular galleries are stored
     "promote_jupyter_magic": True,
    #  'doc_module': ('PyDune'),  # Modules for which function/class level galleries are created.
    #  'reference_url': {'PyDune': None,  # The module you locally document uses None
    #                    'numpy': 'https://docs.scipy.org/doc/numpy/',
    #                    'scipy': 'https://docs.scipy.org/doc/scipy/reference/',
    #                    'matplotlib': 'https://matplotlib.org/stable'},
    "capture_repr": ("_repr_html_", "__repr__"),
    "matplotlib_animations": True,
    'plot_gallery': False,
    "nested_sections": True,
    "show_api_usage": False,
    'show_memory': True,
    # "reset_modules": ("matplotlib", "seaborn", "sg_doc_build.reset_others"),
    # 'ignore_repr_types': r'matplotlib\.(text|axes)',
     }


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_templates"]

coverage_show_missing_items = True
autosummary_generate = True  # Turn on sphinx.ext.autosummary
templates_path = ["_templates"]
# autodoc_member_order = "bysource"

# Strip input prompts from copied code
# copybutton_prompt_text = ">>> "
# copybutton_prompt_text = (
#     r">>> |^\d+|\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
# )
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]

def hide_sg_links(app, pagename, templatename, context, doctree):
    if pagename.startswith("auto_examples/"):
        app.add_css_file("hide_links.css")

def setup(app):
    # ...
    app.connect("html-page-context", hide_sg_links)

html_baseurl = "https://wavesongs.github.io/"
html_theme = 'pydata_sphinx_theme'
html_css_files = ["css/custom.css"]

html_theme_options = {
    # "navigation_with_keys": True,

    "repository_url": "https://github.com/wavesongs/wavesongs",
    "repository_branch": "main",
    "path_to_docs": "./",
    "use_repository_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "home_page_in_toc": False,
    "use_issues_button": True,
    "show_navbar_depth": 1,
    "max_navbar_depth": 3,
    "show_toc_level": 3,
    "sidebarwidth": "50px",
    "collapse_navbar": False,
    "secondary_sidebar_items": ["page-toc", "sg_download_links", "sg_launcher_links"],
    "launch_buttons": {
        "colab_url": "https://colab.research.google.com",
        # "binderhub_url": " https://mybinder.org/",
        # "deepnote_url": "https://deepnote.com"
    },
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": "https://github.com/wavesongs/wavesongs",  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-square-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        }
    ],
    "secondary_sidebar_items": ["page-toc", "sg_download_links", "sg_launcher_links"],
    # "logo_only": True,
    # "extra_navbar": False,
}

# html_logo = "path/to/myimage.png"
html_title = "WaveSongs"


autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "special-members": "__init__",
    "member-order": "bysource",
}


suppress_warnings = ["mystnb.unknown_mime_type"]
