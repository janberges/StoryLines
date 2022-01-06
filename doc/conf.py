# Configuration file for the Sphinx documentation builder.

# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = 'StoryLines'
copyright = '2016-2022 Jan Berges'
author = 'Jan Berges'

extensions = ['sphinx.ext.autodoc', 'numpydoc', 'm2r2']

html_theme = 'alabaster'

numpydoc_show_class_members = False
