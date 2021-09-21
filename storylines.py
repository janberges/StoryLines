#!/usr/bin/env python3

from __future__ import division

__version__ = '0.4'

import math
import os
import re
import subprocess

def order_of_magnitude(x):
    """Calculate the decimal order of magnitude.

    Parameters
    ----------
    x : float
        Number of which to calculate the decimal order of magnitude.

    Returns
    -------
    int
        Order of magnitude of `x`.
    """
    return int(math.floor(math.log10(abs(x)))) if x else 0

def power_of_ten(x):
    """Calculate the power of ten of the same order of magnitude.

    Parameters
    ----------
    x : float
        Number of which to calculate the power of ten of the same order of
        magnitude.

    Returns
    -------
    float
        Power of ten of the same order of magnitude as `x`.
    """
    return 10 ** order_of_magnitude(x)

def xround(x, divisor=1):
    """Round to multiple of given number.

    Parameters
    ----------
    x : float
        Number to round.
    divisor : float
        Number the result shall be a multiple of.

    Returns
    -------
    float
        `x` rounded to the closest multiple of `divisor`.
    """
    return divisor * round(x / divisor)

def xround_mantissa(x, divisor=1):
    """Round mantissa to multiple of given number.

    The mantissa is the part before the power of ten in scientific notation.

    Parameters
    ----------
    x : float
        Number the mantissa of which to round.
    divisor : float
        Number the rounded mantissa shall be a multiple of.

    Returns
    -------
    float
        `x` with the mantissa rounded to the closest multiple of `divisor`.
    """
    return xround(x, divisor * power_of_ten(x))

def multiples(lower, upper, divisor=1):
    """Iterate over all integer multiples of given number on closed interval.

    Parameters
    ----------
    lower, upper : float
        Bounds of closed interval.
    divisor : float
        Number the results shall be multiples of.

    Yields
    ------
    float
        Multiple of `divisor` between `lower` and `upper`.
    """
    for n in range(int(math.ceil(lower / divisor)),
            int(math.floor(upper / divisor)) + 1):
        yield divisor * n

def relevant(points, error=1e-3):
    """Remove irrelevant vertices of linear spline.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    error : float, optional
        Tolerated deviation from original spline.

    Yields
    ------
    2-tuple
        Relevant vertex.
    """
    if len(points) < 3:
        for point in points:
            yield point
        return

    i = 0

    def included(angle):
        return upper is None \
            or lower is None \
            or (angle - lower) % (2 * math.pi) \
            <= (upper - lower) % (2 * math.pi)

    while True:
        origin = points[i]
        yield origin

        former = 0.0

        upper = None
        lower = None

        while True:
            x = points[i + 1][0] - origin[0]
            y = points[i + 1][1] - origin[1]

            r = math.sqrt(x ** 2 + y ** 2)
            phi = math.atan2(y, x)

            if r < former or not included(phi):
                break

            i += 1

            if i == len(points) - 1:
                yield points[i]
                return

            former = r

            if r > error:
                delta = math.asin(error / r)

                if included(phi + delta):
                    upper = phi + delta

                if included(phi - delta):
                    lower = phi - delta

def islands(N, criterion, join=False):
    """Select subranges of integer range.

    Parameters
    ----------
    N : integer
        Length of original range.
    criterion : function
        Selection criterion for range members.
    join : bool
        Concatenate all subranges?

    Yields
    ------
    list of int
        Elements of subrange.
    """
    island = []

    for n in range(N):
        if criterion(n):
            island.append(n)

        elif island and not join:
            yield island
            island = []

    if island:
        yield island

def fatband(points, width, weights, shifts, nib=None):
    """Represent weighted data points via varying linewidth.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    width : float
        Overall linewidth scaling factor.
    weights : list of float
        Weights of `points`.
    shifts : list of float
        Displacements in weight direction.
    nib : float
        Angle of broad pen nib. If ``None``, the nib is held perpendicular to
        the direction of the line. The direction is always the average of the
        directions of adjacent line segments.

    Returns
    -------
    list of 2-tuple
        Fatband outline.

    See Also
    --------
    miter_butt : Equivalent routine with miter line join.
    """
    N = len(points)

    x, y = tuple(zip(*points))

    if nib is not None:
        alpha = [nib] * (N - 1)
    else:
        alpha = [(math.pi / 2 + math.atan2(y[n + 1] - y[n], x[n + 1] - x[n]))
            % (2 * math.pi) for n in range(N - 1)]

    phi = alpha[:1]

    for n in range(N - 2):
        phi.append(sum(alpha[n:n + 2]) / 2)

        if max(alpha[n:n + 2]) - min(alpha[n:n + 2]) > math.pi:
            phi[-1] += math.pi

    phi.append(alpha[-1])

    X = []
    Y = []

    for sgn in 1, -1:
        for n in range(N) if sgn == 1 else reversed(range(N)):
            X.append(x[n] + math.cos(phi[n]) * width
                * (shifts[n] + sgn * weights[n] / 2))
            Y.append(y[n] + math.sin(phi[n]) * width
                * (shifts[n] + sgn * weights[n] / 2))

    return list(zip(X, Y))

def miter_butt(points, width, weights, shifts, nib=None):
    """Represent weighted data points via varying linewidth.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    width : float
        Overall linewidth scaling factor.
    weights : list of float
        Weights of `points`.
    shifts : list of float
        Displacements in weight direction.
    nib : float
        Angle of broad pen nib. If ``None``, the nib is held perpendicular to
        the direction of the current line segment. Line segments are connected
        using the miter joint.

    Returns
    -------
    list of 2-tuple
        Fatband outline.

    See Also
    --------
    fatband : Equivalent routine without miter line join.
    """
    N = len(points)

    x, y = tuple(zip(*points))

    upper = []
    lower = []

    for n in range(N - 1):
        if nib is not None:
            alpha = nib
        else:
            alpha = math.atan2(y[n + 1] - y[n], x[n + 1] - x[n]) + math.pi / 2

        dx = 0.5 * width * math.cos(alpha)
        dy = 0.5 * width * math.sin(alpha)

        lower.append((x[n] - dx, y[n] - dy, x[n + 1] - dx, y[n + 1] - dy))
        upper.append((x[n] + dx, y[n] + dy, x[n + 1] + dx, y[n + 1] + dy))

    X = []
    Y = []

    for segs in upper, lower:
        X.append([segs[0][0]])
        Y.append([segs[0][1]])

        for n in range(1, N - 1):
            x1a, y1a, x1b, y1b = segs[n - 1]
            x2a, y2a, x2b, y2b = segs[n]

            dx1 = x1b - x1a
            dy1 = y1b - y1a

            dx2 = x2b - x2a
            dy2 = y2b - y2a

            det = dy1 * dx2 - dx1 * dy2

            if det:
                X[-1].append((x1a * dy1 * dx2 - y1a * dx1 * dx2
                    - x2a * dx1 * dy2 + y2a * dx1 * dx2) / det)

                Y[-1].append((x1a * dy1 * dy2 - y1a * dx1 * dy2
                    - x2a * dy1 * dy2 + y2a * dy1 * dx2) / det)
            else:
                X[-1].append(x2a)
                Y[-1].append(y2a)

        X[-1].append(segs[-1][2])
        Y[-1].append(segs[-1][3])

    XA = []
    XB = []
    YA = []
    YB = []

    for n in range(N):
        a1 = 0.5 + shifts[n] - 0.5 * weights[n]
        a2 = 0.5 - shifts[n] + 0.5 * weights[n]
        b1 = 0.5 + shifts[n] + 0.5 * weights[n]
        b2 = 0.5 - shifts[n] - 0.5 * weights[n]

        XA.append(a1 * X[0][n] + a2 * X[1][n])
        XB.append(b1 * X[0][n] + b2 * X[1][n])

        YA.append(a1 * Y[0][n] + a2 * Y[1][n])
        YB.append(b1 * Y[0][n] + b2 * Y[1][n])

    return list(zip(XA + XB[::-1], YA + YB[::-1]))

def shortcut(points, length=None, length_rel=1):
    """Cut off loops at self-intersection points.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    length : float
        Maximum length of loop to be cut off.
    length_rel : float
        Maximum length of loop to be cut off relative to the total length of
        the curve.

    Returns
    -------
    list of 2-tuple
        Linear spline with self-intersection loops removed.
    """
    x, y = tuple(zip(*points))

    N = len(x)

    shortcuts = []

    dx = [x[i + 1] - x[i] for i in range(N - 1)]
    dy = [y[i + 1] - y[i] for i in range(N - 1)]

    dist = [0]
    for a, b in zip(dx, dy):
        dist.append(dist[-1] + math.sqrt(a * a + b * b))

    if length is None:
        length = dist[-1]

    length = min(length, length_rel * dist[-1])

    end = [d + length for d in dist]

    i = 0
    while i < N - 1:
        for j in range(i + 2, N - 1):
            if dist[j] > end[i]:
                break

            det = dy[i] * dx[j] - dx[i] * dy[j]

            if det:
                dxij = x[j] - x[i]
                dyij = y[j] - y[i]

                u = (dx[j] * dyij - dy[j] * dxij) / det

                if 0 < u <= 1:
                    v = (dx[i] * dyij - dy[i] * dxij) / det

                    if 0 <= v < 1:
                        if u == 1 and v == 0 and N > 4 == len(shortcut(
                            [(x[k], y[k]) for k in (i, i + 2, j - 1, j + 1)])):
                            print('Preserve non-crossing intersection '
                                '(%.2g, %.2g)' % (x[j], y[j]))
                            continue

                        shortcuts.append((i, j,
                            x[i] + u * dx[i], y[i] + u * dy[i]))

                        looplen = (
                            (dist[j + 1] * v + dist[j] * (1 - v)) -
                            (dist[i + 1] * u + dist[i] * (1 - u)))

                        print('Remove loop (%.2gcm, %.2g%%)'
                            % (looplen, looplen / dist[-1] * 100))

                        i = j
                        break
        i += 1

    x = list(x)
    y = list(y)

    for i, j, x0, y0 in reversed(shortcuts):
        x[i + 1:j + 1] = [x0]
        y[i + 1:j + 1] = [y0]

    return list(zip(x, y))

def cut(points, minimum=None, maximum=None, join=False):
    """Cut off curve segments beyond y interval.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    minimum, maximum : float, default None
        Lower and upper bound of y interval.
    join : bool
        Concatenate remaining curve segments?

    Yields
    ------
    list of 2-tuple
        Remaining curve segment.

    See Also
    --------
    cut : Similar function for 2D case.
    """
    points = [tuple(point) for point in points]

    for y in minimum, maximum:
        if y is None:
            continue

        n = 0 if join else 1

        while n < len(points):
            x1, y1 = points[n - 1]
            x2, y2 = points[n]

            if y1 < y < y2 or y1 > y > y2:
                x = (x1 * (y2 - y) + x2 * (y - y1)) / (y2 - y1)
                points.insert(n, (x, y))

            n += 1

    for island in islands(len(points), lambda n:
            (minimum is None or points[n][1] >= minimum) and
            (maximum is None or points[n][1] <= maximum), join):

        yield [points[n] for n in island]

def cut2d(points, xmin, xmax, ymin, ymax, join=False):
    """Cut off curve segments beyond x and y intervals.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    xmin, xmax : float
        Lower and upper bound of x interval.
    ymin, ymax : float
        Lower and upper bound of y interval.
    join : bool
        Concatenate remaining curve segments?

    Yields
    ------
    list of 2-tuple
        Remaining curve segment.

    See Also
    --------
    cut : Similar function for 1D case.
    """
    for group in cut(points, ymin, ymax, join):
        group = [(y, x) for x, y in group]

        for group in cut(group, xmin, xmax, join):
            group = [(x, y) for y, x in group]

            yield group

def jump(points, distance=1.0):
    """Interpret long line segments as discontinuities and omit them.

    Parameters
    ----------
    points : list of 2-tuple
        Vertices of linear spline.
    distance : float
        Shortest line segment to be omitted.

    Yields
    ------
    list of 2-tuple
        Separated curve segment.
    """
    points = [tuple(point) for point in points]

    group = []

    for n in range(len(points)):
        if group:
            x1, y1 = points[n - 1]
            x2, y2 = points[n]

            if (x2 - x1) ** 2 + (y2 - y1) ** 2 > distance ** 2:
                yield group
                group = [points[n]]
                continue

        group.append(points[n])

    if group:
        yield group

def groups(iterable, size=4):
    """Group sequence of objects into chunks of given size.

    Parameters
    ----------
    iterable : iterable
        Iterable sequence of objects.
    size : int
        Group size.

    Yields
    ------
    list
        Group of objects.
    """
    group = []

    for item in iterable:
        group.append(item)

        if len(group) == size:
            yield group
            group = []

    if group:
        yield group

def csv(options):
    """Format TikZ options.

    Parameters
    ----------
    options : dict
        TikZ options, where spaces in keys are represented by underscores.

    Returns
    -------
    str
        Comma-separated key-value pairs in TikZ format.
    """
    return ', '.join(key.replace('_', ' ')
        + ('' if value is True else '=%s' % value)
        for key, value in sorted(options.items())
        if value is not False and value is not None)

def goto(filename):
    """Go to output directory for plot typesetting.

    Parameters
    ----------
    filename : str
        LaTeX file name including possible path.

    Returns
    -------
    stem : str
        File name without path and extension.
    typeset : function
        Function to run ``pdflatex`` and remove ``.aux`` and ``.log`` files.
    home : function
        Function to return to previous working directory.
    """
    head, tail = os.path.split(filename)
    stem = tail[:-4] if tail.endswith(('.tex', '.pdf')) else tail

    if head:
        cwd = os.getcwd()
        subprocess.call(['mkdir', '-p', head])
        os.chdir(head)

    def typeset():
        try:
            subprocess.call(['pdflatex', '--interaction=batchmode',
                '%s.tex' % stem])

            for suffix in 'aux', 'log':
                os.remove('%s.%s' % (stem, suffix))

        except OSError:
            print('pdflatex not found')

    def home():
        if head:
            os.chdir(cwd)

    return stem, typeset, home

pt = 2.54 / 72.27 # cm

class Plot():
    """Plot object.

    Notes
    -----

    In all textual attributes and parameters, numbers in angle brackets are
    interpreted as values in y data units, e.g., ``line_width='<0.1>'``. For
    the parameters `line_width` and `mark_size` this is also the case if an
    integer or float is passed instead of a string.

    Parameters
    ----------
    width : float, default 8.0
         Figure width in cm. A negative value is interpreted as the inner width
         (without left and right margins). If zero, the x-axis scale is set
         equal to the y-axis scale and the width is inferred from the height.
    height : float, default 6.0
         Figure height in cm. A negative value is interpreted as the innter
         height (without bottom and top margins). If zero, the y-axis scale is
         set equal to the x-axis scale and the height is inferred from the
         width.
    margin : float, default None
        Default margin in cm. If ``None``, margins are set automatically. This
        is not always the best option.
    xyaxes : bool, default True
        Draw x and y axes?
    style : str, default None
        Predefined style. Possible values are ``'Nature'``, ``'NatCommun'``,
        and ``'APS'``. This changes some of the below default values.
    **more
        Global TikZ options.

    Attributes
    ----------
    left : float, default `margin`
        Left margin in cm.
    right : float, default `margin`
        Right margin in cm.
    bottom : float, default `margin`
        Bottom margin in cm.
    top : float, default `margin`
        Top margin in cm.
    margmin : float, default 0.15
        Minimum automatic margin in cm.
    xlabel, ylabel, zlabel : str, default None
        Axis labels.
    xticks, yticks, zticks : list, default None
        List of ticks, e.g., ``[0, (0.5, '$\\\\frac12$'), 1]``.
    xspacing, yspacing, zspacing : float, default 1.0
        Approximate tick spacing in cm.
    xstep, ystep, zstep : float, default None
        Exact tick increment.
    xmin, ymin, zmin : float, default None
        Lower axis limit.
    xmax, ymax, zmax : float, default None
        Upper axis limit.
    xpadding, ypadding, zpadding : float, default 0.0
        Padding between data and axes in data units.
    xclose, yclose, zclose : bool, default False
        Place axis labels in space reserved for tick labels.
    xformat, yformat, zformat : function
        Tick formatter. Takes tick position as argument.
    lower : str, default 'blue'
        Lower color of colorbar.
    upper : str, default 'red'
        Upper color of colorbar.
    title : str, default None
        Plot title.
    label : str, default None
        Subfigure label, e.g., ``'a'``.
    labelsize : int, default None
        Different font size for subfigure label in pt.
    labelformat : function, default None
        Formatter for subfigure label. Takes `label` as argument.
    lali : str, default 'center'
        Alignment of legend entries.
    lbls : str, default '\\\\\\\\baselineskip'
        Line height of legend entries.
    lbox : bool, default False
        Draw box around legend?
    lcol : int, default 1
        Number of columns in legend.
    llen : str, default '4mm'
        Length of example lines next to labels.
    lopt : str, default None
        Legend options, e.g., for orientation.
    lpos : str, default 'cm'
        Legend position, a combination of ``lcrbmtLCRBMT`` or a tuple of data
        coordinates.
    lput : bool, default True
        Draw legend?
    lrow : int, default 0
        Number of rows in legend.
    lsep : str, default None
        Space between legend title and entries, e.g., ``'6pt'``.
    ltop : str, default None
        Legend title.
    lwid : float, default 4.0
        Width of legend columns in units of `llen`.
    tick : str, default 0.07
        Length of tick marks in cm.
    gap : float, default 0.0
        Gap between plot area and colorbar in cm.
    tip : float, default 0.1
        Overlap of axis tips in cm.
    xaxis : bool, default `xyaxes`
        Draw x axis?
    yaxis : bool, default `xyaxes`
        Draw y axis?
    frame : bool, default `xyaxes`
        Draw frame around plot area?
    colorbar : bool or str, default None
        Draw colorbar? If ``None``, the colobar is drawn if any line is given a
        z value or if both `zmin` and `zmax` are given. Alternatively, the path
        to an image with a color gradient can be specified. Here, an image
        width of one pixel is sufficient.
    outline : bool, default False
        Draw dashed figure outline?
    background : str, default None
        Path to background image.
    preamble : str, default ''
        Definitions for standalone figures.
    inputenc : str, default None
        Text endocing, e.g., ``'utf8'``.
    fontenc : str
        Font endocing. The default is ``'T1'`` if `font` is specified, ``None``
        otherwise.
    font : str, default None
        Prefined font selection. Imitates well-known fonts. Possible values are
        ``'Gill Sans'``, ``'Helvetica'``, ``'Iwona'``, ``'Latin Modern'``, and
        ``'Times'``.
    fontsize : int, default 10
        Font size for standalone figures in pt.
    lines : list
        List of all line objects.
    options : dict
        Global TikZ options.
    """
    def __init__(self, width=8.0, height=6.0, margin=None, xyaxes=True,
            style=None, **more):

        self.width = width
        self.height = height

        self.left = margin
        self.right = margin
        self.bottom = margin
        self.top = margin

        self.margmin = 0.15

        for x in 'xyz':
            setattr(self, x + 'label', None)
            setattr(self, x + 'ticks', None)
            setattr(self, x + 'spacing', 1.0)
            setattr(self, x + 'step', None)
            setattr(self, x + 'min', None)
            setattr(self, x + 'max', None)
            setattr(self, x + 'padding', 0.0)
            setattr(self, x + 'close', False)
            setattr(self, x + 'format',
                lambda x: ('%g' % x).replace('-', '\\smash{\\llap\\textminus}'))

        self.lower = 'blue'
        self.upper = 'red'

        self.title = None

        self.label = None
        self.labelsize = None
        self.labelformat = None

        self.lali = 'center'
        self.lbls = '\\baselineskip'
        self.lbox = False
        self.lcol = 1
        self.llen = '4mm'
        self.lopt = None
        self.lpos = 'cm'
        self.lput = True
        self.lrow = 0
        self.lsep = None
        self.ltop = None
        self.lwid = 4.0

        self.tick = 0.07
        self.gap = 0.0
        self.tip = 0.1

        self.xaxis = xyaxes
        self.yaxis = xyaxes
        self.frame = xyaxes
        self.colorbar = None
        self.outline = False

        self.background = None

        self.preamble = ''
        self.inputenc = None
        self.fontenc = None
        self.font = None
        self.fontsize = 10

        self.lines = []

        self.options = dict(
            line_cap='round',
            line_join='round',
            mark_size='0.05cm')

        if style is not None:
            if style == 'Nature':
                self.font = 'Helvetica'
                self.fontsize = 7
                self.labelsize = 8
                self.labelformat = lambda x: '\\textbf{%s}' % x
                self.single = 8.9
                self.double = 18.3

            if style == 'NatCommun':
                self.font = 'Helvetica'
                self.fontsize = 8
                self.labelsize = 9
                self.labelformat = lambda x: '\\textbf{%s}' % x
                self.single = 8.8
                self.double = 18.0

            elif style == 'APS':
                self.font = 'Times'
                self.labelformat = lambda x: '(%s)' % x
                self.single = 8.6
                self.double = 17.8

        for name, value in more.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                self.options[name] = value

    def line(self,
            x = [],
            y = [],
            z = None,

            axes = False,
            code = None,
            cut = False,
            frame = False,
            join = None,
            jump = 0,
            label = None,
            miter = False,
            nib = None,
            omit = True,
            protrusion = 0,
            sgn = +1,
            shifts = None,
            shortcut = 0,
            shortcut_rel = 0.5,
            thickness = 1,
            weights = None,
            xref = None,
            yref = None,
            zindex = None,

            **options):
        """Add line/curve.

        Parameters
        ----------
        x, y : list or float
            Coordinates of data points.
        z : float, default None
            z value for entire line, represented by color.
        axes : bool, default False
            Draw axes at current z index? By default, the axes are drawn on top
            of all data.
        code : str, default None
            Literal TikZ code to be inserted at current position.
        cut : bool, default False
            Cut off line segments beyond plotting range?
        frame : bool, default False
            Draw frame at current z index? By default, the frame is drawn just
            below the axes.
        join : bool, default None
            Join cut-up line segments along edge of plotting range? By default,
            this is ``True`` if any ``fill`` is specified, ``False`` otherwise.
        jump : float, default 0
            Shortest distance between consecutive data points that is
            considered as a discontinuity.
        label : str, default None
            Label for legend entry.
        miter : bool, default False
            Draw fatbands using `miter_butt` function? If ``False``, the
            `fatband` function is used.
        nib : float, default None
            Angle of broad pen nib. If ``None``, the nib is held perpendicular
            to the direction of the current line segment.
        omit : bool, default True
            Remove irrelevant vertices of linear spline?
        protrusion : float, default 0
            Extend curve linearly at both ends? This may improve the appearance
            of fatbands ending at the edge of the plotting range.
        sgn : integer, default +1
            Direction of fatband outline. Coinciding outlines should be drawn
            in the same direction if `omit` is ``True``.
        shifts : list of float
            Displacements in weight direction of fatband.
        shortcut : float, default 0
            Maximum length of loop to be cut off.
        shortcut_rel : float, default 0.5
            Maximum length of loop to be cut off relative to the total length
            of the curve. This is only used if `shortcut` is nonzero.
        thickness : float, default 1
            Overall fatband linewidth scaling factor.
        weights : list of float
            Fatband weights.
        xref, yref : float, default None
            Reference values for filled curves. This is useful to visualize
            integrands such as a density of states.
        zindes : int, default None
            Index of list of lines where new line is inserted. By default, the
            new line is appended to the list, i.e., has the highest `zindex`.
        **options
            Local TikZ options.
        """
        if not hasattr(x, '__len__'):
            x = [x]

        if not hasattr(y, '__len__'):
            y = [y]

        new_line = dict(
            x = x,
            y = y,
            z = z,

            axes = axes,
            code = code,
            cut = cut,
            frame = frame,
            join = join,
            jump = jump,
            label = label,
            miter = miter,
            nib = nib,
            omit = omit,
            protrusion = protrusion,
            sgn = sgn,
            shifts = shifts,
            shortcut = shortcut,
            shortcut_rel = shortcut_rel,
            thickness = thickness,
            weights = weights,
            xref = xref,
            yref = yref,

            options = options,
            )

        if zindex is None:
            self.lines.append(new_line)
        else:
            self.lines.insert(zindex, new_line)

    def fatband(self, x, y, weights=1.0, shifts=0.0, **options):
        """Draw fatband.

        Parameters
        ----------
        x, y : list
            Vertices of linear spline.
        weights : list of float or float
            Weights of `x` and `y`.
        shifts : list of float or float
            Displacements in weight direction.
        **options
            Options passed to `line` function.
        """
        try:
            iter(weights)
        except TypeError:
            weights = [weights] * len(x)
        try:
            iter(shifts)
        except TypeError:
            shifts = [shifts] * len(x)

        for island in islands(len(weights),
            lambda n: any(weights[max(n - 1, 0):n + 2])):

            if len(island) > 1:
                n = slice(island[0], island[-1] + 1)
                self.line(x[n], y[n], weights=weights[n], shifts=shifts[n],
                    **options)

    def compline(self, x, y, weights=1.0, colors=True, threshold=0.0,
            **options):
        """Represent points of multiple weights as composite fatband.

        Parameters
        ----------
        x, y : list of float
            Coordinates of line vertices.
        weights : list of tuple of float, list of float, or float, default 1.0
            Weights of vertices. The corresponding linewidth is always measured
            perpendicular to the direction of the line; This ensures that lines
            of the same weight have the same thickness regardless of direction.
        colors : list of str or str, default True
            Colors of different components. Any objects whose representations
            as a string are valid LaTeX colors can be used. If ``True``, the
            fill color is the same as the stroke color.
        threshold : float, default 0.0
            Minimum displayed weight.
        **options
            Further line options.
        """
        try:
            weights = [[0 if part < threshold else part for part in parts]
                for parts in weights]
        except TypeError:
            try:
                weights = [[0 if part < threshold else part]
                    for part in weights]
            except TypeError:
                weights = [[0 if weights < threshold else weights]] * len(x)

        try:
            iter(colors)
        except TypeError:
            colors = [colors] * len(x)

        shifts = []

        for parts in weights:
            shifts.append([0])
            shift = shifts[-1]

            for part in parts:
                shift.append(shift[-1] + part)

            for m, part in enumerate(parts):
                shift[m] -= (shift[-1] - part) / 2

        sgn = +1
        for weights, shifts, color in zip(zip(*weights), zip(*shifts), colors):
            self.fatband(x, y, weights, shifts, fill=color, sgn=sgn, **options)
            sgn *= -1

    def node(self, x, y, content, name=None, **options):
        """Draw (text) node at given position.

        Parameters
        ----------
        x, y : float
            Node position in data coordinates.
        content : str
            Node content.
        name : str
            Name/label to refer back to the node.
        **options
            TikZ options of the node, e.g., ``above left=True``.
        """
        self.code('\n\t\\node %s[%s] at (<x=%.14g>, <y=%.14g>) {%s};'
            % ('(%s) ' % name if name else '', csv(options), x, y, content))

    def cut(self, x=0.0, y=0.0):
        """Indicate broken axis.

        Parameters
        ----------
        x, y : float
            Position of the break symbol.
        """
        self.axes()
        for cmd, color, to in ('fill', 'white', '--'), ('draw', 'black', '  '):
            self.code('\n\t\\%s [%s, xshift=<x=%.14g>cm, yshift=<y=%.14g>cm] '
                '(-0.1, -0.15) -- (0.1, 0.05) %s (0.1, 0.15) -- (-0.1, -0.05);'
                % (cmd, color, x, y, to))

    def point(self, x, y, name):
        """Define point.

        Parameters
        ----------
        x, y : float
            Point position in data coordinates.
        name : str
            Name/label to refer back to the point.
        """
        self.code('\n\t\\coordinate (%s) at (<x=%.14g>, <y=%.14g>);'
            % (name, x, y))

    def code(self, data, **options):
        """Insert literal TikZ code.

        Parameters
        ----------
        data : str
            TikZ code. Positions and distances in data coordinates and units
            can be specified using angle brackets, e.g., ``(<x=1>, <y=2>)`` or
            ``+(<dx=1>, <dy=2>)``.
        **options
            Options passed to `line`.
        """
        self.line(code=data, **options)

    def axes(self, **options):
        """Draw axes at current position."""

        self.line(axes=True, **options)

    def clear(self):
        """Remove all lines from plot."""

        self.lines = []

    def save(self, filename, external=False, standalone=False, pdf=False):
        """Save plot to file.

        Parameters
        ----------
        filename : str
            File name. If no period is contained, the ``.tex`` extension
            may be omitted.
        external : bool, default False
            Provide file name to TikZ library ``external``.
        standalone : bool, default False
            Create file that can be typeset with ``pdflatex``, i.e., include
            document header etc.?
        pdf : bool, default False
            Typeset TeX file via ``pdflatex``? This implies `standalone`.
        """
        if pdf:
            standalone = True

        # determine data limits:

        lower = {}
        upper = {}

        for x in 'xyz':
            xmin = getattr(self, x + 'min')
            xmax = getattr(self, x + 'max')

            if xmin is None or xmax is None:
                if x == 'z':
                    X = [line[x] for line in self.lines if line[x] is not None]

                else:
                    X = [value for line in self.lines for value in line[x]]

            if x == 'z' and self.colorbar is None:
                self.colorbar = xmin is not None and xmax is not None or bool(X)

            lower[x] = xmin if xmin is not None else min(X) if X else 0.0
            upper[x] = xmax if xmax is not None else max(X) if X else 0.0

            lower[x] -= getattr(self, x + 'padding')
            upper[x] += getattr(self, x + 'padding')

        # handle horizontal and vertical lines:

        for x, y in 'xy', 'yx':
            for line in self.lines:
                if not len(line[x]) and len(line[y]) == 1:
                    line[x] = [lower[x], upper[x]]
                    line[y] = [line[y][0]] * 2

                    line['options'].setdefault('line_cap', 'butt')

        # choose automatic margins:

        baselineskip = 1.2 * self.fontsize * pt

        if self.bottom is None:
            self.bottom = self.margmin

            if self.xaxis:
                xticks = self.xticks is None or bool(self.xticks)

                if self.xlabel or xticks:
                    self.bottom += self.tick + baselineskip

                if self.xlabel and xticks and not self.xclose:
                    self.bottom += baselineskip

        if self.left is None:
            self.left = self.margmin

            if self.yaxis:
                yticks = self.yticks is None or bool(self.yticks)

                if self.ylabel or yticks:
                    self.left += self.tick + baselineskip

                if self.ylabel and yticks and not self.yclose:
                    self.left += baselineskip

        if self.right is None:
            self.right = self.margmin

            if self.colorbar:
                self.right += self.tip

                zticks = self.zticks is None or bool(self.zticks)

                if self.zlabel or zticks:
                    self.right += baselineskip

                if self.zlabel and zticks and not self.zclose:
                    self.right += baselineskip

        if self.top is None:
            self.top = self.margmin

            if self.title:
                self.top += baselineskip

        # interpret negative as inner dimensions:

        if self.width < 0:
            self.width = -self.width + self.left + self.right

        if self.height < 0:
            self.height = -self.height + self.bottom + self.top

        # determine extent of the plotting area:

        extent = {}
        extent['x'] = self.width - self.left - self.right
        extent['y'] = self.height - self.bottom - self.top

        # determine width or height for proportional plot:

        if not self.height:
            extent['y'] = (upper['y'] - lower['y']) * extent['x'] \
                        / (upper['x'] - lower['x'])
            self.height = extent['y'] + self.bottom + self.top

        elif not self.width:
            extent['x'] = (upper['x'] - lower['x']) * extent['y'] \
                        / (upper['y'] - lower['y'])
            self.width = extent['x'] + self.left + self.right

        # take care of z-axis:

        extent['z'] = extent['y']

        # determine scale and tick positions

        scale = {}
        ticks = {}

        for x in extent.keys():
            # embed zero- and one-dimensional data

            if lower[x] == upper[x]:
                padding = power_of_ten(lower[x])

                lower[x] -= padding
                upper[x] += padding

            # how many centimeters correspond to one unit of the axis?

            scale[x] = extent[x] / (upper[x] - lower[x])

            # use ticks or choose ticks with a spacing close to the given one

            xformat = getattr(self, x + 'format')

            if getattr(self, x + 'ticks') is not None:
                ticks[x] = [(scale[x] * (n - lower[x]), label) for n, label in
                    [tick if hasattr(tick, '__len__') else (tick, xformat(tick))
                        for tick in getattr(self, x + 'ticks')]]
            else:
                ticks[x] = [(scale[x] * (n - lower[x]), xformat(n))
                    for n in multiples(lower[x], upper[x],
                        getattr(self, x + 'step') or xround_mantissa(
                        getattr(self, x + 'spacing') / scale[x]))]

        # build LaTeX file

        labels = []

        stem, typeset, home = goto(filename)

        with open('%s.tex' % stem, 'w') as file:
            # print premable and open document

            if standalone:
                file.write('\\documentclass[class=%s, %dpt, '
                    'varwidth=\\maxdimen]{standalone}\n'
                    % ('article' if 10 <= self.fontsize <= 12 else 'scrartcl',
                        self.fontsize))
                file.write('\\usepackage{tikz}\n')

                if self.inputenc and 'inputenc' not in self.preamble:
                    file.write('\\usepackage[%s]{inputenc}\n' % self.inputenc)

                if self.font is not None:
                    file.write({
                        'Gill Sans':
                            '\\usepackage[math]{iwona}\n'
                            '\\usepackage[sfdefault]{cabin}\n'
                            '\\usepackage[italic]{mathastext}\n',
                        'Helvetica':
                            '\\usepackage{sansmathfonts}\n'
                            '\\usepackage[scaled]{helvet}\n'
                            '\\let\\familydefault\sfdefault\n'
                            '\\usepackage[italic]{mathastext}\n',
                        'Iwona':
                            '\\usepackage[math]{iwona}\n',
                        'Latin Modern':
                            '\\usepackage{lmodern}\n',
                        'Times':
                            '\\usepackage{newtxtext, newtxmath}\n',
                        }[self.font])

                    if self.fontenc is None:
                        self.fontenc = 'T1'

                if self.fontenc and 'fontenc' not in self.preamble:
                    file.write('\\usepackage[%s]{fontenc}\n' % self.fontenc)

                if self.preamble:
                    file.write('%s\n' % self.preamble.strip())

                for line in self.lines:
                    if ('mark' in line['options'] and line['options']['mark']
                            not in ['*', '+', 'x', 'ball']):
                        file.write('\\usetikzlibrary{plotmarks}\n')
                        break

                file.write('\\begin{document}\n\\noindent\n' )

            # set filename for externalization

            elif external:
                file.write('\\tikzsetnextfilename{%s}\n%%\n' % stem)

            # open TikZ environment

            file.write('\\begin{tikzpicture}[%s]' % csv(self.options))

            # set bounding box

            file.write('\n\t\\draw [use as bounding box, %s]'
                % ('gray, very thin, dashed' if self.outline else 'draw=none'))

            file.write('\n\t\t(%.3f, %.3f) rectangle +(%.3f, %.3f);'
                % (-self.left, -self.bottom, self.width, self.height))

            # add background image

            if self.background is not None:
                file.write('\n\t\\node '
                    '[anchor=south west, inner sep=0, outer sep=0] '
                    '{\includegraphics[width=%.3fcm, height=%.3fcm]{%s}};'
                    % (extent['x'], extent['y'], self.background))

            def draw_frame():
                if draw_frame.done:
                    return

                file.write('\n\t\\draw [gray, line cap=rect]\n\t\t')

                if not self.xaxis:
                    file.write('(0, 0) -- ')

                file.write('(%.3f, 0) -- (%.3f, %.3f) -- (0, %.3f)'
                        % tuple(extent[x] for x in 'xxyy'))

                if not self.yaxis:
                    file.write(' -- (0, 0)')

                file.write(';')

                draw_frame.done = True

            draw_frame.done = False

            def draw_axes():
                if draw_axes.done:
                    return

                # paint colorbar

                if self.colorbar:
                    if isinstance(self.colorbar, str):
                        file.write('\n\t\\node at (%.3f, 0) '
                            '[anchor=south west, inner sep=0, outer sep=0] '
                            '{\includegraphics[width=%.3fcm, height=%.3fcm]'
                            '{%s}};' % (extent['x'] + self.gap,
                                self.tip - self.gap, extent['y'],
                                self.colorbar))
                    else:
                        file.write('\n\t\\shade [bottom color=%s, top color=%s]'
                            % (self.lower, self.upper))

                        file.write('\n\t\t(%.3f, 0) rectangle (%.3f, %.3f);'
                            % (extent['x'] + self.gap,
                               extent['x'] + self.tip,
                               extent['z']))

                    for z, label in ticks['z']:
                        file.write('\n\t\\node '
                            '[rotate=90, below] at (%.3f, %.3f) {%s};'
                            % (extent['x'] + self.tip, z, label))

                if self.frame:
                    draw_frame()

                if self.xaxis or self.yaxis:
                    # draw tick marks and labels

                    if self.xaxis and ticks['x'] or self.yaxis and ticks['y']:
                        file.write('\n\t\\draw [line cap=butt]')

                        if self.xaxis:
                            for x, label in ticks['x']:
                                file.write('\n\t\t(%.3f, 0) -- +(0, %.3f) '
                                    'node [below] {%s}'
                                    % (x, -self.tick, label))

                        if self.yaxis:
                            for y, label in ticks['y']:
                                file.write('\n\t\t(0, %.3f) -- +(%.3f, 0) '
                                    'node [rotate=90, above] {%s}'
                                    % (y, -self.tick, label))

                        file.write(';')

                    # draw coordinate axes

                    file.write('\n\t\\draw [%s-%s, line cap=butt]\n\t\t'
                        % ('<' * (self.xaxis and not self.colorbar),
                            '>' * self.yaxis))

                    if self.xaxis:
                        file.write('(%.3f, 0) -- ' % (extent['x'] + self.tip))

                    file.write('(0, 0)')

                    if self.yaxis:
                        file.write(' -- (0, %.3f)' % (extent['y'] + self.tip))

                    file.write(';')

                # label coordinate axes

                if self.xaxis and self.xlabel:
                    file.write('\n\t\\node [below')

                    if ticks['x'] and not self.xclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (extent['x'] / 2, -self.tick))

                    file.write('\n\t\t{%s};' % self.xlabel)

                if self.yaxis and self.ylabel:
                    file.write('\n\t\\node [rotate=90, above')

                    if ticks['y'] and not self.yclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (-self.tick, extent['y'] / 2))

                    file.write('\n\t\t{%s};' % self.ylabel)

                if self.colorbar and self.zlabel:
                    file.write('\n\t\\node [rotate=90, below')

                    if ticks['z'] and not self.zclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (extent['x'] + self.tip, extent['y'] / 2))

                    file.write('\n\t\t{%s};' % self.zlabel)

                draw_axes.done = True

            draw_axes.done = False

            # plot lines

            form = '(%%%d.3f, %%%d.3f)' % (
                5 if extent['x'] < 10 else 6,
                5 if extent['y'] < 10 else 6)

            for line in self.lines:
                if line['z'] is not None:
                    ratio = (line['z'] - lower['z']) / (upper['z'] - lower['z'])

                    line['options'].setdefault('color',
                        '%s!%.1f!%s' % (self.upper, 100 * ratio, self.lower))

                    if line['options'].get('mark') == 'ball':
                        line['options'].setdefault('ball_color',
                            line['options']['color'])

                for option in 'line_width', 'mark_size':
                    if isinstance(line['options'].get(option), (float, int)):
                        line['options'][option] = ('%.3fcm'
                            % (line['options'][option] * scale['y']))

                for option in line['options']:
                    if isinstance(line['options'][option], str):
                        line['options'][option] = re.sub('<([\d.]+)>',
                            lambda match: '%.3f' % (float(match.group(1))
                                * scale['y']), line['options'][option])

                if line['label'] is not None:
                    labels.append([line['options'], line['label']])

                if len(line['x']) and len(line['y']):
                    for x, y in 'xy', 'yx':
                        xref = line[x + 'ref']

                        if xref is not None:
                            line[x] = list(line[x])
                            line[y] = list(line[y])

                            line[x] =      [xref] + line[x] + [xref]
                            line[y] = line[y][:1] + line[y] + line[y][-1:]

                    points = list(zip(*[[scale[x] * (n - lower[x])
                        for n in line[x]] for x in 'xy']))

                    if line['protrusion']:
                        for i, j in (1, 0), (-2, -1):
                            if line['weights'] is not None:
                                if not line['weights'][j]:
                                    continue

                            dx = points[j][0] - points[i][0]
                            dy = points[j][1] - points[i][1]
                            dr = math.sqrt(dx * dx + dy * dy)
                            rescale = 1 + line['protrusion'] / dr

                            points[j] = (
                                points[i][0] + dx * rescale,
                                points[i][1] + dy * rescale,
                                )

                    if line['jump']:
                        segments = jump(points, distance=line['jump'])
                    else:
                        segments = [points]

                    if line['weights'] is not None:
                        segments = [(miter_butt if line['miter'] else fatband)(
                            segment, line['thickness'], line['weights'],
                            line['shifts'], line['nib']) for segment in segments]

                    if line['cut']:
                        if line['join'] is None:
                            line['join'] = (line['options'].get('fill')
                                is not None)

                        if line['options'].get('only_marks'):
                            segments = [[(x, y)
                                for segment in segments
                                for x, y in segment
                                if  0 <= x <= extent['x']
                                and 0 <= y <= extent['y']]]
                        else:
                            segments = [segment
                                for segment in segments
                                for segment in cut2d(segment,
                                    0, extent['x'], 0, extent['y'],
                                        line['join'])]

                    for segment in segments:
                        if line['omit']:
                            segment = relevant(segment[::line['sgn']])

                        elif line['cut'] and line['options'].get('mark') \
                                and not line['options'].get('only_marks'):

                            line['options']['mark_indices'] \
                                = '{%s}' % ','.join(str(n)
                                    for n, point in enumerate(segment, 1)
                                    if point in points)

                        if line['shortcut']:
                            segment = shortcut(segment, line['shortcut'],
                                line['shortcut_rel'])

                        file.write('\n\t\\draw [%s] plot coordinates {'
                            % csv(line['options']))

                        for group in groups(segment):
                            file.write('\n\t\t')
                            file.write(' '.join(form % point
                                for point in group))

                        file.write(' };')

                # insert TikZ code with special coordinates:

                if line['code']:
                    code = line['code']

                    for x in 'xy':
                        code = re.sub('<%s=(.*?)>' % x, lambda match: '%.3f'
                            % (scale[x] * (float(match.group(1)) - lower[x])),
                            code)

                        code = re.sub('<d%s=(.*?)>' % x, lambda match: '%.3f'
                            % (scale[x] * float(match.group(1))),
                            code)

                    file.write(code)

                if line['axes']:
                    draw_axes()

                if line['frame']:
                    draw_frame()

            draw_axes()

            # add label

            if self.label is not None:
                if self.labelformat is not None:
                    self.label = self.labelformat(self.label)

                if self.labelsize is not None:
                    self.label = ('\\fontsize{%d}{%d}\\selectfont %s' %
                        (self.labelsize, self.labelsize, self.label))

                file.write('\n\t\\node at (current bounding box.north west) '
                    '[inner sep=0pt, below right] {%s};'
                    % self.label)

            # add legend

            if self.lput and (self.ltop is not None or labels):
                if isinstance(self.lpos, str):
                    x = []
                    y = []

                    positions = dict(
                        L = (x, -self.left),
                        B = (y, -self.bottom),
                        l = (x, 0.0),
                        b = (y, 0.0),
                        r = (x, extent['x']),
                        t = (y, extent['y']),
                        R = (x, extent['x'] + self.right),
                        T = (y, extent['y'] + self.top),
                        )

                    abbreviations = dict(c='lr', C='LR', m='bt', M='BT')

                    for abbreviation in abbreviations.items():
                        self.lpos = self.lpos.replace(*abbreviation)

                    for char in self.lpos:
                        positions[char][0].append(positions[char][1])

                    x = sum(x) / len(x)
                    y = sum(y) / len(y)
                else:
                    x, y = self.lpos
                    x = scale['x'] * (x - lower['x'])
                    y = scale['y'] * (y - lower['y'])

                file.write('\n\t\\node [align=%s' % self.lali)

                if self.lopt is not None:
                    file.write(', %s' % self.lopt)

                if self.lbox:
                    file.write(', draw, fill=white, rounded corners')

                file.write('] at (%.3f, %.3f) {' % (x, y))

                if self.ltop:
                    file.write('\n\t\t\\tikzset{sharp corners}')
                    file.write('\n\t\t%s' % self.ltop)

                    if labels:
                        file.write(' \\\\')

                        if self.lsep is not None:
                            file.write('[%s]' % self.lsep)

                if labels:
                    file.write('\n\t\t\\begin{tikzpicture}[x=%s, y=-%s]'
                        % (self.llen, self.lbls))

                    lrow = self.lrow or 1 + (len(labels) - 1) // self.lcol

                    for n, (options, label) in enumerate(labels):
                        col = n // lrow
                        row = n %  lrow

                        if label:
                            file.write('\n\t\t\t\\node '
                                '[right] at (%.3f, %d) {%s};'
                                % (col * self.lwid + 1, row, label))

                        draw  = not options.get('only_marks')
                        draw &= not options.get('draw') == 'none'
                        mark = 'mark' in options

                        if draw or mark:
                            if draw and mark:
                                options['mark_indices'] = '{2}'

                            file.write('\n\t\t\t\\draw [%s]' % csv(options))
                            file.write('\n\t\t\t\tplot coordinates ')

                            if draw and mark:
                                x = [0.0, 0.5, 1.0]
                            elif draw:
                                x = [0.0, 1.0]
                            elif mark:
                                x = [0.5]

                            file.write('{')

                            for m in range(len(x)):
                                file.write(' (%.3f, %d)'
                                    % (col * self.lwid + x[m], row))

                            file.write(' };')

                    file.write('\n\t\t\\end{tikzpicture}%')

                file.write('\n\t\t};')

            # add title:

            if self.title is not None:
                file.write('\n\t\\node [above] at (%.3f, %.3f) {%s};'
                    % (extent['x'] / 2, extent['y'], self.title))

            # close TikZ environment

            file.write('\n\\end{tikzpicture}%')

            # close document

            if standalone:
                file.write('\n\\end{document}')

            file.write('\n')

        # typeset document and clean up:

        if pdf:
            typeset()

        home()

def combine(filename, pdfs, columns=100, align=0.5, pdf=False):
    """Arrange multiple PDFs in single file.

    Parameters
    ----------
    filename : str
        Name of combined file.
    pdfs : list of str
        Names of PDFs to be combined.
    columns : int, default 100
        Number of PDFs to be arranged side by side.
    align : float, default 0.5
        Vertical alignment of PDFs, where 0, 0.5, and 1 stand for the bottom,
        center, and top of the individual figures.
    pdf : bool, default False
        Convert resulting TeX file to PDF?
    """
    stem, typeset, home = goto(filename)

    with open('%s.tex' % stem, 'w') as tex:
        tex.write('\\documentclass[varwidth=\maxdimen]{standalone}\n'
            '\\usepackage{graphicx}\n'
            '\\begin{document}\n'
            '\\noindent%\n')

        for n in range(len(pdfs)):
            tex.write('\\raisebox{-%g\\height}{\\includegraphics{{%s}.pdf}}%s\n'
                % (align, pdfs[n], '%' if (n + 1) % columns else '\\\\[-\\lineskip]'))

        tex.write('\\end{document}\n')

    if pdf:
        typeset()

    home()

def dot(A, B):
    """Calculate dot product of two vectors.

    Parameters
    ----------
    A, B : list of float
        Vectors to be multiplied.

    Returns
    -------
    float
        Dot product of `A` and `B`.
    """
    return sum(a * b for a, b in zip(A, B))

def cross(A, B):
    """Calculate cross product of two vectors.

    Parameters
    ----------
    A, B : list of float
        Vectors to be multiplied.

    Returns
    -------
    float
        Cross product of `A` and `B`.
    """
    return [
        A[1] * B[2] - A[2] * B[1],
        A[2] * B[0] - A[0] * B[2],
        A[0] * B[1] - A[1] * B[0],
        ]

def projection(
        r=[0.0,  0.0, 0.0], # object
        R=[0.0, -1.0, 0.0], # observer
        T=[0.0,  0.0, 0.0], # target
        U=[0.0,  0.0, 1.0], # up
        ):
    """Project 3D point onto 2D screen.

    Parameters
    ----------
    T : list of float
        Object position.
    R : list of float
        Observer position.
    T : list of float
        Viewing direction (from observer).
    U : list of float
        Vertical direction.

    Returns
    -------
    list of float
        x and y position as well as proximity factor z.
    """
    # viewing direction:
    Z = [b - a for a, b in zip(R, T)]
    norm = math.sqrt(dot(Z, Z))
    Z = [z / norm for z in Z]

    # horizontal screen direction:
    X = cross(Z, U)
    norm = math.sqrt(dot(X, X))
    X = [x / norm for x in X]

    # vertical screen direction:
    Y = cross(X, Z)

    # observer-object distance vector:
    D = [b - a for a, b in zip(R, r)]

    # observer-object distance (hypotenuse):
    hyp = math.sqrt(dot(D, D))

    # projection onto viewing direction (adjacent leg):
    adj = dot(D, Z)

    # secans of angle of object w.r.t. viewing direction:
    sec = hyp / adj

    # horizontal screen coordinate:
    x = dot(X, D) / adj

    # vertical screen coordinate:
    y = dot(Y, D) / adj

    # magnification factor ("zoom", "z-index"):
    z = sec / adj

    return [x, y, z]

def project(objects, *args, **kwargs):
    """Project list of 3D objects onto 2D screen.

    Line width, mark sizes, and length in angle brackets are scaled according
    to the distance from the observer. The objects are sorted by distance so
    that close object overlay remote objects.

    Parameters
    ----------
    objects : list of tuple
        List of objects. Each object is represented by a tuple, which consists
        of a list of three-tuples ``(x, y, z)`` and a style dictionary.

    *args, **kwargs
        Arguments passed to `projection`.

    Returns
    -------
    list of tuple
        Objects is same format, but sorted with transformed coordinates and
        adjusted styles.
    """
    objects = [([projection(coordinate, *args, **kwargs)
        for coordinate in coordinates], style.copy())
        for coordinates, style in objects]

    zoom = [sum(coordinate[2]
        for coordinate in coordinates) / len(coordinates)
        for coordinates, style in objects]

    for n, (coordinates, style) in enumerate(objects):
        for option in 'line_width', 'mark_size':
            if isinstance(style.get(option), (float, int)):
                style[option] *= zoom[n]

        for option in style:
            if isinstance(style[option], str):
                style[option] = re.sub('(?<=<)([\d.]+)(?=>)', lambda match:
                    '%.3f' % (float(match.group(1)) * zoom[n]), style[option])

    order = sorted(range(len(zoom)), key=lambda n: zoom[n])

    return [objects[n] for n in order]

def bonds(R1, R2, d1=0.0, d2=0.0, dmin=0.1, dmax=5.0):
    """Find lines that connect two sets of points.

    Parameters
    ----------
    R1, R2 : list of tuple
        Two (ordered) sets of points.
    d1, d2 : float
        Shortening on the two line ends.
    dmin, dmax : float
        Minimum and maximum line length.

    Returns
    -------
    list of list of tuple
        Connecting lines.
    """
    bonds = []

    oneway = R1 is R2

    for n, r1 in enumerate(R1):
        for m, r2 in enumerate(R2):
            if oneway and m <= n:
                continue

            dr = [b - a for a, b in zip(r1, r2)]
            d = math.sqrt(dot(dr, dr))

            if dmin < d < dmax:
                s1 = d1 / d
                s2 = d2 / d

                bonds.append([
                    [(1 - s1) * a + s1 * b for a, b in zip(r1, r2)],
                    [s2 * a + (1 - s2) * b for a, b in zip(r1, r2)],
                    ])

    return bonds
