# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Line plots with Python & TikZ."""

__version__ = '0.9'

from .plot import Plot
from .calc import (order_of_magnitude, power_of_ten, xround, xround_mantissa,
    multiples, dot, cross, bonds)
from .color import Color, colormap, colorize, HSV2RGB, RGB2HSV, PSV2RGB
from .convert import inch, pt, csv
from .cut import relevant, shortcut, cut, cut2d, jump
from .fatband import fatband, miter_butt
from .files import goto, typeset, rasterize, combine
from .group import islands, groups
from .png import save, load
from .proj import projection, project
