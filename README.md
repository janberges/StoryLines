# Line plots with Python & TikZ

StoryLines is a Python library to create plots in LaTeX format.

* `plot` - figure object
* `calc` - mathematical helpers
* `color` - blendable colors and colormaps
* `convert` - inches to centimeters etc.
* `cut` - remove redundant or unwanted points
* `fatband` - plot weights along line
* `files` - typeset TeX, rasterize PDF
* `group` - chunk sequences of points
* `png` - save and load RGB(A) graphics
* `proj` - project 3D object onto plane

## Installation

Optionally using a virtual environment:

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip

Either from PyPI:

    python3 -m pip install storylines

Or from the repository:

    git clone https://github.com/janberges/StoryLines
    python3 -m pip install -e StoryLines

## Documentation

The documentation and example scripts along with output can be found at
<https://janberges.github.io/StoryLines>.

Note that `storylines.module.member` is equivalent to `storylines.member`.

## License

This program is free software under the terms of the BSD Zero Clause License.

Copyright (C) 2016-2024 Jan Berges
