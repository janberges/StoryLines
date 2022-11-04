# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Figure object."""

from __future__ import division

import math
import re

from .calc import power_of_ten, xround_mantissa, multiples
from .color import Color, colormap, colorize
from .convert import inch, pt, csv
from .cut import relevant, shortcut, cut2d, jump
from .fatband import fatband, miter_butt
from .files import goto, typeset, rasterize
from .group import islands, groups
from .png import save

class Plot():
    """Plot object.

    Parameters
    ----------
    width : float, default None
         Figure width in cm. A negative value is interpreted as the inner width
         (without left and right margins). If zero, the x-axis scale is set
         equal to the y-axis scale and the width is inferred from the height. By
         default, the single-column width for the chosen `style` is used.
    height : float, default None
         Figure height in cm. A negative value is interpreted as the inner
         height (without bottom and top margins). If zero, the y-axis scale is
         set equal to the x-axis scale and the height is inferred from the
         width. By default, it is inferred from `width` for a 4:3 aspect ratio.
    margin : float, default None
        Default margin in cm. If ``None``, margins are set automatically. This
        is not always the best option.
    xyaxes : bool, default True
        Draw x and y axes?
    style : str, default None
        Predefined style. Possible values are ``'Nature'``, ``'NatCommun'``,
        and ``'APS'``. This changes some of the below default values.
    rounded : bool, default True
        Use ``round`` as default value for ``line cap`` and ``line join``?
        Otherwise the TikZ initial values ``miter`` and ``butt`` are used.
    **more
        Initial values of attributes (see below) or global TikZ options.

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
    ratio : float, default None
        Figure width divided by figure height. The desired aspect ratio is
        obtained by adding extra margins as needed.
    align : float, default 0.5
        If `ratio` is used, this value aligns the original plot relative to the
        new viewport. A value of ``0.0``, ``0.5``, and ``1.0`` moves it to the
        lower side, to the center, and to the upper side, respectively.
    xlabel, ylabel, zlabel : str, default None
        Axis labels.
    xticks, yticks, zticks : list, default None
        List of ticks, e.g., ``[0, (0.5, '$\\\\frac12$'), 1]``. If the label is
        ``None``, the tick mark is not drawn (but possibe grid lines are).
    xmarks, ymarks, zmarks : bool, default True
        Show tick marks and labels?
    xspacing, yspacing, zspacing : float, default 1.0
        Approximate tick spacing in cm.
    xstep, ystep, zstep : float, default None
        Exact tick increment.
    xmin, ymin, zmin : float, default None
        Lower axis limit.
    xmax, ymax, zmax : float, default None
        Upper axis limit.
    dleft, dright, dbottom, dtop : float, default 0.0
        Protrusion of x- and y-axis limits into margins in cm.
    xpadding, ypadding, zpadding : float, default 0.0
        Padding between data and axes in data units.
    xclose, yclose, zclose : bool, default False
        Place axis labels in space reserved for tick labels.
    xformat, yformat, zformat : function
        Tick formatter. Takes tick position as argument.
    lower : str, default 'blue'
        Lower color of colorbar. Can also be of type ``Color`` as long as
        `upper` has the same type.
    upper : str, default 'red'
        Upper color of colorbar. Can also be of type ``Color`` as long as
        `lower` has the same type.
    cmap : function, default None
        Colormap for colorbar used instead of `lower` and `upper`.
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
    gap : float, default 0.15
        Gap between plot area and colorbar in cm.
    bar : float, default 0.15
        Width of color bar in cm.
    tip : float, default 0.1
        Overlap of axis tips in cm.
    xaxis : bool, default `xyaxes`
        Draw x axis?
    yaxis : bool, default `xyaxes`
        Draw y axis?
    frame : bool, default `xyaxes`
        Draw frame around plot area?
    grid : bool, default False
        Add grid lines (at tick positions)?
    colorbar : bool or str, default None
        Draw colorbar? If ``None``, the colorbar is drawn if any line is given a
        z value or if both `zmin` and `zmax` are given. Alternatively, the path
        to an image with a color gradient can be specified. Here, an image width
        of one pixel is sufficient.
    outline : bool, default False
        Draw dashed figure outline?
    canvas : str, default None
        Background color of whole document.
    background : str, default None
        Path to background image.
    preamble : str, default ''
        Definitions for standalone figures.
    inputenc : str, default None
        Text encoding, e.g., ``'utf8'``.
    fontenc : str, default None
        Font encoding. The default is ``'T1'`` if `font` is specified, none
        otherwise.
    font : str, default None
        Predefined font selection. Imitates well-known fonts. Possible values
        are ``'Gill Sans'``, ``'Helvetica'``, ``'Iwona'``, ``'Latin Modern'``,
        and ``'Times'``.
    fontsize : int, default 10
        Font size for standalone figures in pt.
    single : float, default 8.0
        Single-column width for the chosen `style`.
    double : float, default 17.0
        Full textwidth for the chosen `style`.
    resolution : float, default 1e-3
        Smallest distance in cm expected to be discernible when looking at the
        plot. The default is acceptable when the plot is viewed or printed in
        its original size. For zooming, smaller values may be necessary. This
        parameter determines the number of vertices used to render a line and
        thus affects the file size.
    lines : list
        List of all line objects.
    options : dict
        Global TikZ options.

    Notes
    -----
    In all textual attributes and parameters, numbers in angle brackets are
    interpreted as values in y data units, e.g., ``line_width='<0.1>'``. For
    the parameters `line_width` and `mark_size` this is also the case if an
    integer or float is passed instead of a string.
    """
    def __init__(self, width=None, height=None, margin=None, xyaxes=True,
            style=None, rounded=True, **more):

        self.width = width
        self.height = height

        self.left = margin
        self.right = margin
        self.bottom = margin
        self.top = margin

        self.dleft = 0.0
        self.dright = 0.0
        self.dbottom = 0.0
        self.dtop = 0.0

        self.margmin = 0.15

        self.ratio = None
        self.align = 0.5

        for x in 'xyz':
            setattr(self, x + 'label', None)
            setattr(self, x + 'ticks', None)
            setattr(self, x + 'marks', True)
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
        self.cmap = None

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
        self.gap = 0.15
        self.bar = 0.15
        self.tip = 0.1

        self.xaxis = xyaxes
        self.yaxis = xyaxes
        self.frame = xyaxes
        self.grid = False
        self.colorbar = None
        self.outline = False
        self.canvas = None

        self.background = None

        self.preamble = ''
        self.inputenc = None
        self.fontenc = None
        self.font = None
        self.fontsize = 10

        self.single = 8.0
        self.double = 17.0

        self.resolution = 1e-3

        self.lines = []

        self.options = dict(mark_size='0.05cm')

        if rounded:
            self.options.update(line_cap='round', line_join='round')

        if style is not None:
            if style == 'Nature':
                self.font = 'Helvetica'
                self.fontsize = 7
                self.labelsize = 8
                self.labelformat = lambda x: '\\textbf{%s}' % x
                self.single = 8.9
                self.double = 18.3

            elif style == 'NatCommun':
                self.font = 'Helvetica'
                self.fontsize = 8
                self.labelsize = 9
                self.labelformat = lambda x: '\\textbf{%s}' % x
                self.single = 8.8
                self.double = 18.0

            elif style == 'APS':
                self.font = 'Times'
                self.fontsize = 9
                self.labelformat = lambda x: '(%s)' % x
                self.single = 8.6
                self.double = 17.8

        if self.width is None:
            self.width = self.single

        if self.height is None:
            self.height = 3 * self.width / 4

        for name, value in more.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                self.options[name] = value

    def line(self,
            x=[],
            y=[],
            z=None,

            axes=False,
            code=None,
            cut=False,
            frame=False,
            grid=False,
            join=None,
            jump=0,
            label=None,
            miter=False,
            nib=None,
            omit=None,
            protrusion=0,
            sgn=+1,
            shifts=None,
            shortcut=0,
            shortcut_rel=0.5,
            thickness=0.05,
            weights=None,
            xref=None,
            yref=None,
            zindex=None,

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
        cut : bool or tuple, default False
            Cut off line segments beyond plotting range? It is also possible to
            pass the clipping window as a tuple ``(xmin, xmax, ymin, ymax)`` in
            data coordinates, where ``None`` is replaced by the plot bounds.
        frame : bool, default False
            Draw frame at current z index? By default, the frame is drawn just
            below the axes.
        grid : bool, default False
            Add grid lines (at tick positions) at current z index? By default,
            the grid is drawn just below the frame.
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
        omit : bool, default None
            Remove irrelevant vertices of linear spline? The default is
            ``False`` if the TikZ option ``mark`` is set, ``True`` otherwise.
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
        thickness : float, default 0.05
           Fatband linewidth in cm.
        weights : list of float
            Fatband weights.
        xref, yref : float, default None
            Reference values for filled curves. This is useful to visualize
            integrands such as a density of states.
        zindex : int, default None
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
            x=x,
            y=y,
            z=z,

            axes=axes,
            code=code,
            cut=cut,
            frame=frame,
            grid=grid,
            join=join,
            jump=jump,
            label=label,
            miter=miter,
            nib=nib,
            omit=omit,
            protrusion=protrusion,
            sgn=sgn,
            shifts=shifts,
            shortcut=shortcut,
            shortcut_rel=shortcut_rel,
            thickness=thickness,
            weights=weights,
            xref=xref,
            yref=yref,

            options=options,
            )

        if zindex is None:
            self.lines.append(new_line)
        else:
            self.lines.insert(zindex, new_line)

    def fatband(self, x, y, weights=1.0, shifts=0.0, fill=True, draw='none',
            **options):
        """Draw fatband.

        Parameters
        ----------
        x, y : list
            Vertices of linear spline.
        weights : list of float or float, default 1.0
            Weights of `x` and `y`.
        shifts : list of float or float, default 0.0
            Displacements in weight direction.
        fill, draw : str or Color
            TikZ line options (filled without outline by default).
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
                    fill=fill, draw=draw, **options)

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
        self.code('\\node%s%s at (<x=%.14g>, <y=%.14g>) {%s};'
            % (' (%s)' % name if name else '', csv(options), x, y, content))

    def cut(self, x=0.0, y=0.0):
        """Indicate broken axis.

        Parameters
        ----------
        x, y : float
            Position of the break symbol.
        """
        self.axes()
        for cmd, color, to in ('fill', 'white', '--'), ('draw', 'black', '  '):
            self.code('\\%s [%s, xshift=<x=%.14g>cm, yshift=<y=%.14g>cm] '
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
        self.code('\\coordinate (%s) at (<x=%.14g>, <y=%.14g>);' % (name, x, y))

    def image(self, filename, x1, y1, x2, y2, **options):
        """Insert image between given data coordinates.

        Parameters
        ----------
        filename : str
            File name of image.
        x1, y1 : float
            Position of bottom-left corner in data coordinates.
        x2, y2 : float
            Position of top-right corner in data coordinates.
        **options
            Options passed to `line`.
        """
        if x1 < x2:
            xscale = 1
        else:
            xscale = -1
            x1, x2 = x2, x1

        if y1 < y2:
            yscale = 1
        else:
            yscale = -1
            y1, y2 = y2, y1

        graphics = (r'\includegraphics[width=<dx=%g>cm, height=<dy=%g>cm]{%s}'
            % (x2 - x1, y2 - y1, filename))

        if not xscale == yscale == 1:
            graphics = r'\scalebox{%s}[%s]{%s}' % (xscale, yscale, graphics)

        self.code('\\node at (<x=%g>, <y=%g>) '
            '[anchor=south west, inner sep=0, outer sep=0] {%s};'
            % (x1, y1, graphics), **options)

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
        """Draw axes at current z index."""

        self.line(axes=True, **options)

    def nolabel(self):
        """Pass empty entry to legend (as spacer between entries)."""

        self.line(draw='none', label='')

    def clear(self):
        """Remove all lines from plot."""

        self.lines = []

    def save(self, filename, external=False, standalone=False, pdf=False,
            png=False, dpi=300.0, width=0, height=0):
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
            Automatically set to ``True`` if `filename` ends with ``.pdf``.
        png : bool, default False
            Rasterize PDF file via ``pdftoppm``? This implies `pdf`.
            Automatically set to ``True`` if `filename` ends with ``.png``.
        dpi : float, default 300.0
            Image resolution in dots per inch.
        width, height : int
            Image dimensions in pixels. If either `width` or `height` is zero,
            it will be determined by the aspect ratio of the image. If both are
            zero, they will also be determined by `dpi`.
        """
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

            # embed zero- and one-dimensional data:

            if lower[x] == upper[x]:
                padding = power_of_ten(lower[x])

                lower[x] -= padding
                upper[x] += padding

        # choose automatic margins:

        baselineskip = 1.2 * self.fontsize * pt

        if self.bottom is None:
            self.bottom = self.margmin

            if self.xaxis:
                xticks = ((self.xticks is None or bool(self.xticks))
                    and self.xmarks)

                if self.xlabel or xticks:
                    self.bottom += self.tick + baselineskip

                if self.xlabel and xticks and not self.xclose:
                    self.bottom += baselineskip

        if self.left is None:
            self.left = self.margmin

            if self.yaxis:
                yticks = ((self.yticks is None or bool(self.yticks))
                    and self.ymarks)

                if self.ylabel or yticks:
                    self.left += self.tick + baselineskip

                if self.ylabel and yticks and not self.yclose:
                    self.left += baselineskip

        if self.right is None:
            self.right = self.margmin

            if self.colorbar:
                self.right += self.gap + self.bar

                zticks = ((self.zticks is None or bool(self.zticks))
                    and self.zmarks)

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

        # temporarily subtract protrusions from margins:

        self.left -= self.dleft
        self.right -= self.dright
        self.bottom -= self.dbottom
        self.top -= self.dtop

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

        # determine scale:

        scale = {}

        for x in extent.keys():
            # how many centimeters correspond to one unit of the axis?

            scale[x] = extent[x] / (upper[x] - lower[x])

        # add protrusions back to margins:

        self.left += self.dleft
        self.right += self.dright
        self.bottom += self.dbottom
        self.top += self.dtop

        lower['x'] += self.dleft / scale['x']
        upper['x'] -= self.dright / scale['x']
        lower['y'] += self.dbottom / scale['y']
        upper['y'] -= self.dtop / scale['y']

        extent['x'] -= self.dleft + self.dright
        extent['y'] -= self.dbottom + self.dtop

        # take care of z-axis:

        extent['z'] = extent['y']
        scale['z'] = extent['z'] / (upper['z'] - lower['z'])

        # set aspect ratio by adjusting margins:

        if self.ratio is not None:
            ratio = self.width / self.height

            if ratio < self.ratio:
                diff = self.height * self.ratio - self.width

                self.width += diff
                self.left += self.align * diff
                self.right += (1 - self.align) * diff

            elif self.ratio < ratio:
                diff = self.width / self.ratio - self.height

                self.height += diff
                self.bottom += self.align * diff
                self.top += (1 - self.align) * diff

        # determine tick positions:

        ticks = {}

        for x in extent.keys():
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

        # handle horizontal and vertical lines:

        for x, y in 'xy', 'yx':
            for line in self.lines:
                if not len(line[x]) and len(line[y]) == 1:
                    line[x] = [lower[x], upper[x]]
                    line[y] = [line[y][0]] * 2

                    line['options'].setdefault('line_cap', 'butt')

        # create simple colormap from special lower and upper colors:

        if self.cmap is None:
            if isinstance(self.upper, Color) and isinstance(self.lower, Color):
                self.cmap = colormap((0, self.lower), (1, self.upper))

        # build LaTeX file

        labels = []

        stem, typ, home = goto(filename)

        png = png or typ == 'png'
        pdf = pdf or typ == 'pdf' or png

        if pdf:
            standalone = True

        with open('%s.tex' % stem, 'w') as file:
            # print premable and open document

            if standalone:
                file.write('\\documentclass[class=%s, %dpt]{standalone}\n'
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
                            '\\usepackage[italic, noplusnominus]{mathastext}\n',
                        'Helvetica':
                            '\\usepackage{sansmathfonts}\n'
                            '\\usepackage[scaled]{helvet}\n'
                            '\\let\\familydefault\\sfdefault\n'
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

                file.write('\\begin{document}\n\\noindent\n')

            # set filename for externalization

            elif external:
                file.write('\\tikzsetnextfilename{%s}\n%%\n' % stem)

            # open TikZ environment

            file.write('\\begin{tikzpicture}%s' % csv(self.options, '[%s]'))

            # set bounding box

            bbox = ('\n  (%.3f, %.3f) rectangle +(%.3f, %.3f);'
                % (-self.left, -self.bottom, self.width, self.height))

            file.write('\n\\useasboundingbox')
            file.write(bbox)

            if self.canvas is not None:
                file.write('\n\\draw%s'
                    % csv(dict(color=self.canvas, line_width='1mm', fill=True)))
                file.write(bbox)

            if self.outline:
                file.write('\n\\draw%s'
                    % csv(dict(color='gray', very_thin=True, dashed=True)))
                file.write(bbox)

            # add background image

            if self.background is not None:
                file.write('\n\\node '
                    '[anchor=south west, inner sep=0, outer sep=0] '
                    '{\includegraphics[width=%.3fcm, height=%.3fcm]{%s}};'
                    % (extent['x'], extent['y'], self.background))

            def draw_grid():
                if draw_grid.done:
                    return

                file.write('\n\\draw [lightgray, line cap=rect]')

                for x, label in ticks['x']:
                    if 0 < x < extent['x']:
                        file.write('\n  (%.3f, 0) -- +(0, %.3f)'
                            % (x, extent['y']))

                for y, label in ticks['y']:
                    if 0 < y < extent['y']:
                        file.write('\n  (0, %.3f) -- +( %.3f, 0)'
                            % (y, extent['x']))

                file.write(';')

                draw_grid.done = True

            draw_grid.done = False

            def draw_frame():
                if draw_frame.done:
                    return

                file.write('\n\\draw [gray, line cap=rect]\n  ')

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
                    if self.cmap is not None:
                        dots = max(2, int(round(extent['z'] / inch * dpi)))

                        colorbar = colorize([[n / (dots - 1.0)]
                            for n in reversed(range(dots))], self.cmap)

                        self.colorbar = '%s.bar.png' % stem

                        save(self.colorbar, colorbar)

                    if isinstance(self.colorbar, str):
                        file.write('\n\\node at (%.3f, 0) '
                            '[anchor=south west, inner sep=0, outer sep=0] '
                            '{\includegraphics[width=%.3fcm, height=%.3fcm]'
                            '{%s}};' % (extent['x'] + self.gap,
                                self.bar, extent['y'], self.colorbar))
                    else:
                        file.write('\n\\shade [bottom color=%s, top color=%s]'
                            % (self.lower, self.upper))

                        file.write('\n  (%.3f, 0) rectangle (%.3f, %.3f);'
                            % (extent['x'] + self.gap,
                               extent['x'] + self.gap + self.bar,
                               extent['z']))

                    if self.zmarks:
                        for z, label in ticks['z']:
                            if label is None:
                                continue

                            file.write('\n\\node '
                                '[rotate=90, below] at (%.3f, %.3f) {%s};'
                                % (extent['x'] + self.gap + self.bar, z, label))

                if self.grid:
                    draw_grid()

                if self.frame:
                    draw_frame()

                if self.xaxis or self.yaxis:
                    # draw tick marks and labels

                    if self.xaxis and ticks['x'] or self.yaxis and ticks['y']:
                        file.write('\n\\draw [line cap=butt]')

                        if self.xaxis and self.xmarks:
                            for x, label in ticks['x']:
                                if label is None:
                                    continue

                                file.write('\n  (%.3f, 0) -- +(0, %.3f) '
                                    'node [below] {%s}'
                                    % (x, -self.tick, label))

                        if self.yaxis and self.ymarks:
                            for y, label in ticks['y']:
                                if label is None:
                                    continue

                                file.write('\n  (0, %.3f) -- +(%.3f, 0) '
                                    'node [rotate=90, above] {%s}'
                                    % (y, -self.tick, label))

                        file.write(';')

                    # draw coordinate axes

                    file.write('\n\\draw [%s-%s, line cap=butt]\n  '
                        % ('<' * self.xaxis, '>' * self.yaxis))

                    if self.xaxis:
                        file.write('(%.3f, 0) -- ' % (extent['x'] + self.tip))

                    file.write('(0, 0)')

                    if self.yaxis:
                        file.write(' -- (0, %.3f)' % (extent['y'] + self.tip))

                    file.write(';')

                # label coordinate axes

                if self.xaxis and self.xlabel:
                    file.write('\n\\node [below')

                    if ticks['x'] and not self.xclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (extent['x'] / 2, -self.tick))

                    file.write('\n  {%s};' % self.xlabel)

                if self.yaxis and self.ylabel:
                    file.write('\n\\node [rotate=90, above')

                    if ticks['y'] and not self.yclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (-self.tick, extent['y'] / 2))

                    file.write('\n  {%s};' % self.ylabel)

                if self.colorbar and self.zlabel:
                    file.write('\n\\node [rotate=90, below')

                    if ticks['z'] and not self.zclose:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, %.3f)'
                        % (extent['x'] + self.gap + self.bar, extent['y'] / 2))

                    file.write('\n  {%s};' % self.zlabel)

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
                        '%s!%.1f!%s' % (self.upper, 100 * ratio, self.lower)
                            if self.cmap is None else self.cmap(ratio))

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
                    label = [line['options'], line['label']]

                    for previous in labels:
                        if label[1] and previous == label:
                            break
                    else:
                        labels.append(label)

                if len(line['x']) and len(line['y']):
                    for x, y in 'xy', 'yx':
                        xref = line[x + 'ref']

                        if xref is not None:
                            line[x] = list(line[x])
                            line[y] = list(line[y])

                            line[x] = [xref] + line[x] + [xref]
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
                            line['shifts'], line['nib'])
                            for segment in segments]

                    if line['cut']:
                        try:
                            xmin, xmax, ymin, ymax = line['cut']
                        except (TypeError, ValueError):
                            xmin = xmax = ymin = ymax = None

                        xmin = (scale['x'] * (xmin - lower['x'])
                            if xmin is not None else 0)

                        xmax = (scale['x'] * (xmax - lower['x'])
                            if xmax is not None else extent['x'])

                        ymin = (scale['y'] * (ymin - lower['y'])
                            if ymin is not None else 0)

                        ymax = (scale['y'] * (ymax - lower['y'])
                            if ymax is not None else extent['y'])

                        if line['join'] is None:
                            line['join'] = (line['options'].get('fill')
                                is not None)

                        if line['options'].get('only_marks'):
                            segments = [[(x, y)
                                for segment in segments
                                for x, y in segment
                                if xmin <= x <= xmax and ymin <= y <= ymax]]
                        else:
                            segments = [segment
                                for segment in segments
                                for segment in cut2d(segment,
                                    xmin, xmax, ymin, ymax, line['join'])]

                    if line['omit'] is None:
                        line['omit'] = 'mark' not in line['options']

                    for segment in segments:
                        if line['omit']:
                            segment = relevant(segment[::line['sgn']],
                                self.resolution)

                        elif line['cut'] and line['options'].get('mark') \
                                and not line['options'].get('only_marks'):

                            line['options']['mark_indices'] \
                                = '{%s}' % ','.join(str(n)
                                    for n, point in enumerate(segment, 1)
                                    if point in points)

                        if line['shortcut']:
                            segment = shortcut(segment, line['shortcut'],
                                line['shortcut_rel'])

                        file.write('\n\\draw%s plot coordinates {'
                            % csv(line['options']))

                        for group in groups(segment):
                            file.write('\n  ')
                            file.write(' '.join(form % point
                                for point in group))

                        file.write(' };')

                # insert TikZ code with special coordinates:

                if line['code']:
                    code = line['code'].strip()

                    for x in 'xy':
                        code = re.sub('<%s=(.*?)>' % x, lambda match: '%.3f'
                            % (scale[x] * (float(match.group(1)) - lower[x])),
                            code)

                        code = re.sub('<d%s=(.*?)>' % x, lambda match: '%.3f'
                            % (scale[x] * float(match.group(1))),
                            code)

                    file.write('\n%s' % code)

                if line['grid']:
                    draw_grid()

                if line['frame']:
                    draw_frame()

                if line['axes']:
                    draw_axes()

            draw_axes()

            # add label

            if self.label is not None:
                if self.labelformat is not None:
                    self.label = self.labelformat(self.label)

                if self.labelsize is not None:
                    self.label = ('\\fontsize{%d}{%d}\\selectfont %s'
                        % (self.labelsize, self.labelsize, self.label))

                file.write('\n\\node at (current bounding box.north west) '
                    '[inner sep=0pt, below right] {%s};' % self.label)

            # add legend

            if self.lput and (self.ltop is not None or labels):
                if isinstance(self.lpos, str):
                    x = []
                    y = []

                    positions = dict(
                        L=(x, -self.left),
                        B=(y, -self.bottom),
                        l=(x, 0.0),
                        b=(y, 0.0),
                        r=(x, extent['x']),
                        t=(y, extent['y']),
                        R=(x, extent['x'] + self.right),
                        T=(y, extent['y'] + self.top),
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

                file.write('\n\\node [align=%s' % self.lali)

                if self.lopt is not None:
                    file.write(', %s' % self.lopt)

                if self.lbox:
                    file.write(', draw, fill=white, rounded corners')

                file.write('] at (%.3f, %.3f) {' % (x, y))

                if self.ltop:
                    file.write('\n  \\tikzset{sharp corners}')
                    file.write('\n  %s' % self.ltop)

                    if labels:
                        file.write(' \\\\')

                        if self.lsep is not None:
                            file.write('[%s]' % self.lsep)

                if labels:
                    file.write('\n  \\begin{tikzpicture}[x=%s, y=-%s]'
                        % (self.llen, self.lbls))

                    lrow = self.lrow or 1 + (len(labels) - 1) // self.lcol

                    spacer = True

                    for n, (options, label) in enumerate(labels):
                        col = n // lrow
                        row = n % lrow

                        if label:
                            file.write('\n    \\node '
                                '[right] at (%.3f, %d) {%s};'
                                % (col * self.lwid + 1, row, label))

                        draw = not options.get('only_marks')
                        draw &= not options.get('draw') == 'none'
                        mark = 'mark' in options

                        if draw or mark:
                            if draw and mark:
                                options['mark_indices'] = '{2}'

                            file.write('\n    \\draw%s' % csv(options))
                            file.write('\n      plot coordinates ')

                            if draw and mark:
                                x = [0.0, 0.5, 1.0]
                                spacer = False
                            elif draw:
                                x = [0.0, 1.0]
                                spacer = False
                            elif mark:
                                x = [0.5]

                            file.write('{')

                            for m in range(len(x)):
                                file.write(' (%.3f, %d)'
                                    % (col * self.lwid + x[m], row))

                            file.write(' };')

                    if spacer:
                        file.write('\n    \\useasboundingbox (0, 0);')

                    file.write('\n  \\end{tikzpicture}%')

                file.write('\n  };')

            # add title:

            if self.title is not None:
                file.write('\n\\node [above] at (%.3f, %.3f) {%s};'
                    % (extent['x'] / 2, extent['y'], self.title))

            # close TikZ environment

            file.write('\n\\end{tikzpicture}%')

            # close document

            if standalone:
                file.write('\n\\end{document}')

            file.write('\n')

        # typeset document and clean up:

        if pdf:
            typeset(stem)

        if png:
            rasterize(stem, dpi, width, height)

        home()
