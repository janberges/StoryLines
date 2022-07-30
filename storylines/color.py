# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Blendable colors and colormaps."""

from __future__ import division

import math

class Color(object):
    """Representation of a color.

    Colors can be defined using different models:

        RGB (red, green, blue):
            The three RGB channels take values from 0 to 255.
        HSV (hue, saturation, value):
            The hue is the color angle in degrees from 0 to 360.
            Values of 0, 120, and 240 correspond to red, green, and blue.
            The saturation takes values from -1 to 1.
            A value of 0 is white; negative values yield complementary colors.
            The value is the RGB amplitude from 0 to 255.
            A value of 0 is black.
        PSV (phase, shift, value):
            Superposition of shifted RGB "waves".
            The phase and the phase shift from R to G (G to B) are in radians.
            The value is the amplitude of the wave from 0 to 255.

    Colors can be mixed:

    .. code-block:: python

        red = Color(255, 0, 0, 'RGB')
        green = Color(120, 1, 255, 'HSV')
        yellow = (red + green) / 2

    Here, colors of different models are converted to RGB first.
    """
    def __init__(self, A, B, C, model='RGB'):
        self.A = A
        self.B = B
        self.C = C
        self.model = model

    context = 'TeX'

    def __str__(self):
        RGB = tuple(map(int, map(round, self.RGB())))

        if self.context == 'TeX':
            return '{rgb,255:red,%d;green,%d;blue,%d}' % RGB

        if self.context == 'HTML':
            return '#%02x%02x%02x' % RGB

        return repr(self)

    def __repr__(self):
        return "Color(%g, %g, %g, '%s')" % (self.A, self.B, self.C, self.model)

    def __add__(i, u):
        if i.model == u.model:
            if i.model == 'RGB':
                return Color(i.A + u.A, i.B + u.B, i.C + u.C)
            if i.model == 'HSV'\
            or i.model == 'PSV':
                if i.C == u.C == 0:
                    return Color((i.A + u.A) / 2, (i.B + u.B) / 2, 0, i.model)

                return Color(
                    (i.A * i.C + u.A * u.C) / (i.C + u.C),
                    (i.B * i.C + u.B * u.C) / (i.C + u.C),
                    i.C + u.C, i.model)
        else:
            return i.toRGB() + u.toRGB()

    def __mul__(i, u):
        if i.model == 'RGB':
            return Color(i.A * u, i.B * u, i.C * u)
        if i.model == 'HSV'\
        or i.model == 'PSV':
            return Color(i.A, i.B, i.C * u, i.model)

    __rmul__ = __mul__

    def __sub__(i, u):
        return i + (-1 * u)

    def __truediv__(i, u):
        return i * u ** -1

    __div__ = __truediv__

    def RGB(self):
        """Calculate red, green, and blue components."""

        if self.model == 'HSV':
            return HSV2RGB(self.A, self.B, self.C)
        elif self.model == 'PSV':
            return PSV2RGB(self.A, self.B, self.C)
        else:
            return self.A, self.B, self.C

    def toRGB(self):
        """Create RGB representation."""

        return Color(*self.RGB())

    def toHSV(self):
        """Create HSV representation."""

        return Color(*RGB2HSV(*self.RGB()), model='HSV')

def colormap(*args):
    """Map interval [0, 1] to colors.

    Colors can be defined for an arbitrary number of points in the interval. In
    between, colors are interpolated linearly. The color for the point ``None``
    is used for NaNs and beyond the outermost points where colors have been
    defined.

    Examples:

    .. code-block:: python

        bluebrown = colormap( # PRB 101, 155107 (2020)
            (0, Color(0.0, 1, 255, 'PSV'), math.sqrt),
            (1, Color(5.5, 1, 255, 'PSV')),
            (None, Color(255, 255, 255, 'RGB')),
            )

        AFMhot = colormap( # Gnuplot
            (0.00, Color(  0,   0,   0)),
            (0.25, Color(128,   0,   0)),
            (0.50, Color(255, 128,   0)),
            (0.75, Color(255, 255, 128)),
            (1.00, Color(255, 255, 255)),
            )
    """
    default = Color(255, 255, 255)
    points = []

    for arg in args:
        if arg[0] is None:
            default = arg[1]
        else:
            points.append((arg[0], arg[1], arg[2] if len(arg) > 2 else None))

    def color(x):
        for n in range(len(color.x) - 1):
            if color.x[n] <= x <= color.x[n + 1]:
                weight = (x - color.x[n]) / (color.x[n + 1] - color.x[n])

                if color.f[n] is not None:
                    weight = color.f[n](weight)

                return (1 - weight) * color.c[n] + weight * color.c[n + 1]

        return default

    color.x, color.c, color.f = tuple(map(list, zip(*points)))

    return color

def colorize(data, cmap=None, minimum=None, maximum=None):
    """Colorize data using colormap.

    Parameters
    ----------
    data : list of list
        Data on two-dimensional mesh.
    cmap : function
        Colormap.
    minimum, maxmimum : float
        Data values corresponding to minimum and maximum of color scale.

    Returns
    -------
    list of list of list
        RGB image.
    """
    height = len(data)
    width = len(data[0])

    data = [x for row in data for x in row]

    if minimum is None:
        minimum = min(x for x in data if not math.isnan(x))

    if maximum is None:
        maximum = max(x for x in data if not math.isnan(x))

    if cmap is None:
        cmap = colormap((0, Color(255, 255, 255)), (1, Color(0, 0, 0)))

    for n, x in enumerate(cmap.x):
        if type(x) is str:
            cmap.x[n] = (float(x) - minimum) / (maximum - minimum)

    data = [(x - minimum) / (maximum - minimum) for x in data]

    data = [min(max(x, 0), 1) for x in data]

    image = []
    for y in range(height):
        image.append([])

        for x in range(width):
            image[-1].append(cmap(data[y * width + x]).RGB())

    return image

def HSV2RGB(H, S=1, V=255):
    """Transform hue, saturation, value to red, green, blue.

    Parameters
    ----------
    H : float
        Hue with period of 360 (degrees).
    S : float
        Saturation between 0 and 1.
    V : float
        Value/brightness between 0 and 255.

    Returns
    -------
    float, float, float
        Red, green, and blue values between 0 an 255.
    """
    if S < 0:
        S = -S
        H += 180

    H %= 360

    h = int(H / 60)
    f = H / 60 - h

    p = V * (1 - S)
    q = V * (1 - S * f)
    t = V * (1 - S * (1 - f))

    if h == 0: return V, t, p
    if h == 1: return q, V, p
    if h == 2: return p, V, t
    if h == 3: return p, q, V
    if h == 4: return t, p, V
    if h == 5: return V, p, q

def RGB2HSV(R, G, B):
    """Transform red, green, blue to hue, saturation, value.

    Parameters
    ----------
    R, G, B : float
        Red, green, and blue values between 0 an 255.

    Returns
    -------
    float
        Hue with period of 360 (degrees).
    float
        Saturation between 0 and 1.
    float
        Value/brightness between 0 and 255.
    """
    V = max(R, G, B)
    extent = V - min(R, G, B)

    if R == G == B:
        H = 0
    elif V == R:
        H = 60 * ((G - B) / extent)
    elif V == G:
        H = 60 * ((B - R) / extent + 2)
    elif V == B:
        H = 60 * ((R - G) / extent + 4)

    S = extent / V if V else 0

    return H, S, V

def PSV2RGB(P, S=1, V=255):
    """Set color via phase, shift, and value.

    Parameters
    ----------
    P : float
        Phase between 0 and 2 pi.
    S : float
        Phase shift from red to green and from green to blue channel between 0
        and 2 pi.
    V : float
        Value/brightness between 0 and 255.

    Returns
    -------
    float, float, float
        Red, green, and blue values between 0 an 255.
    """
    return tuple(V * (0.5 - 0.5 * math.cos(P + S * n)) for n in range(3))
