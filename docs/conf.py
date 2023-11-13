# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "SaagieAPI"
copyright = "2023, Saagie"
author = "Saagie Service Team"

release = "0.1"
version = "0.1.0"

# -- General configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_title = "SaagieAPI"
html_theme = "sphinx_book_theme"
html_theme_options = {"show_toc_level": 2, "toc_title": "On this page"}

# -- Options for EPUB output
epub_show_urls = "footnote"
