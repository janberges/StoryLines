#!/usr/bin/env python

from __future__ import division
from math import asin, atan2, ceil, floor, log10, pi, sqrt

def order_of_magnitude(x):
    return int(floor(log10(abs(x)))) if x else 0

def power_of_ten(x):
    return 10 ** order_of_magnitude(x)

def xround(x, divisor=1):
    return divisor * round(x / divisor)

def xround_mantissa(x, divisor=1):
    return xround(x, divisor * power_of_ten(x))

def multiples(lower, upper, divisor=1):
    for n in range(int(ceil(lower / divisor)), int(floor(upper / divisor)) + 1):
        yield divisor * n

def relevant(points, error=1e-3):
    if len(points) < 3:
        for point in points:
            yield point
        return

    i = 0

    def included(angle):
        return upper is None \
            or lower is None \
            or (angle - lower) % (2 * pi) \
            <= (upper - lower) % (2 * pi)

    while True:
        origin = points[i]
        yield origin

        former = 0.0

        upper = None
        lower = None

        while True:
            x = points[i + 1][0] - origin[0]
            y = points[i + 1][1] - origin[1]

            r = sqrt(x ** 2 + y ** 2)
            phi = atan2(y, x)

            if r < former or not included(phi):
                break

            i += 1

            if i == len(points) - 1:
                yield points[i]
                return

            former = r

            if r > error:
                delta = asin(error / r)

                if included(phi + delta):
                    upper = phi + delta

                if included(phi - delta):
                    lower = phi - delta

def groups(iterable, size=4):
    group = []

    for item in iterable:
        group.append(item)

        if len(group) == size:
            yield group
            group = []

    if group:
        yield group

def csv(options):
    return ', '.join(key.replace('_', ' ')
        + ('' if value is True else '=%s' % value)
        for key, value in options.items()
        if value is not False)

pt = 2.54 / 72 # cm

class Plot():
    def __init__(self, width=10.0, height=6.0, **more):
        self.width = width
        self.height = height

        self.flexible = False

        self.left = 1.0
        self.right = 1.0
        self.bottom = 1.0
        self.top = 0.5

        for x in 'x', 'y', 'z':
            setattr(self, x + 'label', None)
            setattr(self, x + 'ticks', None)
            setattr(self, x + 'format', lambda x: '$%g$' % x)
            setattr(self, x + 'spacing', 1.0)
            setattr(self, x + 'step', None)
            setattr(self, x + 'min', None)
            setattr(self, x + 'max', None)

        self.lower = 'blue'
        self.upper = 'red'

        self.label = None

        self.legend = None
        self.corner = 0
        self.side   = None
        self.margin = 0.2
        self.length = 0.4
        self.box    = False

        self.tick = 0.07
        self.gap = 0.0
        self.tip = 0.1

        self.axes = True
        self.colorbar = True
        self.outline = False

        self.background = None

        self.preamble = None
        self.fontsize = 10

        self.lines = []

        self.options = dict(
            line_cap='round',
            line_join='round',
            mark_size='0.05cm')

        for name, value in more.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                self.options[name] = value

    def line(self, x=[], y=[], z=None, label=None, omit=True,
        xref=None, yref=None, **options):

        self.lines.append(locals())

    def clear(self):
        self.lines = []

    def save(self, filename, external=False, standalone=False):
        # determine extent of the plotting area:

        extent = {}
        extent['x'] = self.width - self.left - self.right
        extent['y'] = self.height - self.bottom - self.top

        # determine data limits (x, y):

        lower = {}
        upper = {}

        for x in 'x', 'y':
            xmin = getattr(self, x + 'min')
            xmax = getattr(self, x + 'max')

            lower[x] = xmin if xmin is not None \
                else min(min(line[x]) for line in self.lines if len(line[x]))

            upper[x] = xmax if xmax is not None \
                else max(max(line[x]) for line in self.lines if len(line[x]))

        # determine width or height for proportional plot:

        if not self.height:
            extent['y'] = (upper['y'] - lower['y']) * extent['x'] \
                        / (upper['x'] - lower['x'])
            self.height = extent['y'] + self.bottom + self.top

        elif not self.width:
            extent['x'] = (upper['x'] - lower['x']) * extent['y'] \
                        / (upper['y'] - lower['y'])
            self.width = extent['x'] + self.left + self.right

        # determine data limits (z):

        z = [line['z'] for line in self.lines if line['z'] is not None]

        if z or self.zmin is not None and self.zmax is not None:
            extent['z'] = extent['y']

            lower['z'] = self.zmin if self.zmin is not None else min(z)
            upper['z'] = self.zmax if self.zmax is not None else max(z)

            colorbar = self.colorbar
        else:
            colorbar = False

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

        with open(filename, 'w') as file:
            # print preable and open document

            if standalone:
                file.write('\\documentclass[%dpt]{scrartcl}\n' % self.fontsize)
                file.write('\\usepackage[paperwidth=%gcm, paperheight=%gcm, '
                    'margin=0cm]{geometry}\n' % (self.width, self.height))
                file.write('\\usepackage{tikz}\n')

                if self.preamble:
                    file.write('%s\n' % self.preamble)

                file.write('\\begin{document}\n\\noindent\n' )

            # set filename for externalization

            elif external:
                file.write('\\tikzsetnextfilename{%s}\n%%\n'
                    % filename.rsplit('.', 1)[0].rsplit('/', 1)[-1])

            # open TikZ environment

            if self.flexible:
                file.write('\\begingroup%%'
                    '\n\\let\\unit\\relax%%'
                    '\n\\newlength\\unit%%'
                    '\n\\setlength\\unit{%g\\linewidth}%%'
                    '\n\\begin{tikzpicture}[x=\\unit, x=\\unit, %s]'
                    % (1.0 / self.width, csv(self.options)))
            else:
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
                    '{ \includegraphics[')

                if self.flexible:
                    file.write('width=%.3f\\unit, height=%.3f\\unit'
                        % (extent['x'], extent['y']))
                else:
                    file.write('width=%.3fcm, height=%.3fcm'
                        % (extent['x'], extent['y']))

                file.write(']{%s} };' % self.background)

            # plot lines

            form = '(%%%d.3f, %%%d.3f)' % (
                5 if extent['x'] < 10 else 6,
                5 if extent['y'] < 10 else 6)

            for line in self.lines:
                if line['z'] is not None and 'color' not in line['options']:
                    ratio = (line['z'] - lower['z']) / (upper['z'] - lower['z'])

                    line['options']['color'] = '%s!%.1f!%s' \
                        % (self.upper, 100 * ratio, self.lower)

                options = csv(line['options'])

                if line['label'] is not None:
                    labels.append([options, line['label']])

                if len(line['x']) and len(line['y']):
                    file.write('\n\t\\draw [%s] plot coordinates {' % options)

                    for x, y in ('x', 'y'), ('y', 'x'):
                        xref = line[x + 'ref']

                        if xref is not None:
                            line[x] = list(line[x])
                            line[y] = list(line[y])

                            line[x] =      [xref] + line[x] + [xref]
                            line[y] = line[y][:1] + line[y] + line[y][-1:]

                    points = list(zip(*[[scale[x] * (n - lower[x])
                        for n in line[x]] for x in ('x', 'y')]))

                    if line['omit']:
                        points = relevant(points)

                    for group in groups(points):
                        file.write('\n\t\t')
                        file.write(' '.join(form % point for point in group))

                    file.write(' };')

            # paint colorbar

            if colorbar:
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

            if self.axes:
                # draw tick marks and labels

                if ticks['x'] or ticks['y']:
                    file.write('\n\t\\draw [line cap=butt]')

                    for x, label in ticks['x']:
                        file.write('\n\t\t(%.3f, 0) -- +(0, %.3f) '
                            'node [below] {%s}'
                            % (x, -self.tick, label))

                    for y, label in ticks['y']:
                        file.write('\n\t\t(0, %.3f) -- +(%.3f, 0) '
                            'node [rotate=90, above] {%s}'
                            % (y, -self.tick, label))

                    file.write(';')

                # draw coordinate axes

                file.write('\n\t\\draw [%s, line cap=butt]'
                    % ('->' if colorbar else '<->'))

                file.write('\n\t\t(%.3f, 0) -- (0, 0) -- (0, %.3f);'
                    % (extent['x'] + self.tip, extent['y'] + self.tip))

            # label coordinate axes

            if self.xlabel:
                file.write('\n\t\\node [below')

                if ticks['x']:
                    file.write('=\\baselineskip')

                file.write('] at (%.3f, %.3f)'
                    % (extent['x'] / 2, -self.tick))

                file.write('\n\t\t{%s};' % self.xlabel)

            if self.ylabel:
                file.write('\n\t\\node [rotate=90, above')

                if ticks['y']:
                    file.write('=\\baselineskip')

                file.write('] at (%.3f, %.3f)'
                    % (-self.tick, extent['y'] / 2))

                file.write('\n\t\t{%s};' % self.ylabel)

            if self.zlabel and colorbar:
                file.write('\n\t\\node [rotate=90, below')

                if ticks['z']:
                    file.write('=\\baselineskip')

                file.write('] at (%.3f, %.3f)'
                    % (extent['x'] + self.tip, extent['y'] / 2))

                file.write('\n\t\t{%s};' % self.zlabel)

            # add label

            if self.label is not None:
                file.write('\n\t\\node [left')

                if ticks['y']:
                    file.write('=\\baselineskip')

                file.write('] at (%.3f, %.3f)'
                    % (-self.tick, extent['y']))

                file.write('\n\t\t{%s};' % self.label)

            # add legend

            if self.legend is not None or labels:
                if self.side is None:
                    left = self.corner in {2, 3}
                    down = self.corner in {3, 4}

                    x, h = (0, 'right') if left else (extent['x'], 'left')
                    y, v = (0, 'above') if down else (extent['y'], 'below')

                    file.write('\n\t\\node [align=center, %s %s=%.3gcm'
                        % (v, h, self.margin))
                else:
                    self.side %= 4

                    s = ['above', 'left', 'below', 'right'][self.side]

                    x = extent['x'] * [0.5, 1.0, 0.5, 0.0][self.side]
                    y = extent['y'] * [0.0, 0.5, 1.0, 0.5][self.side]

                    file.write('\n\t\\node [align=center, %s=%.3gcm'
                        % (s, self.margin))

                if self.box:
                    file.write(', draw, fill=white, rounded corners')

                file.write('] at (%.3f, %.3f) {' % (x, y))

                if self.legend:
                    file.write('\n\t\t\\tikzset{sharp corners}')
                    file.write('\n\t\t%s' % self.legend)

                    if labels:
                        file.write(' \\\\')

                if labels:
                    file.write('\n\t\t\\begin{tikzpicture}'
                        '[x=%.3gcm, y=\\baselineskip, mark indices={2}]'
                        % (0.5 * self.length))

                    for line, (options, label) in enumerate(reversed(labels)):
                        file.write('\n\t\t\t\\node [right] at (2, %d) {%s};'
                            % (line, label))

                        file.write('\n\t\t\t\\draw [%s]' % options)
                        file.write('\n\t\t\t\tplot coordinates '
                            '{ (0, %(n)d) (1, %(n)d) (2, %(n)d) };'
                            % dict(n=line))

                    file.write('\n\t\t\\end{tikzpicture}')

                file.write('\n\t\t};')

            # close TikZ environment

            file.write('\n\\end{tikzpicture}%')

            if self.flexible:
                file.write('\n\\endgroup%')

            # close document

            if standalone:
                file.write('\n\\vspace*{-1pt}\\end{document}')

            file.write('\n')
