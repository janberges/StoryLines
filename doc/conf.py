# Configuration file for the Sphinx documentation builder.

# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = 'StoryLines'
copyright = '2016-2025 Jan Berges'
author = 'Jan Berges'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'numpydoc',
    'myst_parser',
    ]

html_theme = 'sphinx_rtd_theme'
html_logo = '../logo/StoryLines.svg'
html_theme_options = {
    'logo_only': True,
    'style_nav_header_background': '#e7f2fa',
    }

numpydoc_show_class_members = False
