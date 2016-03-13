#!/usr/bin/env python

from math import ceil, floor, log10

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

pt = 2.54 / 72 # cm

class Plot():
    def __init__(self, width=10.0, height=6.0, **more):
        self.width = width
        self.height = height

        self.left = 1.0
        self.right = 1.0
        self.bottom = 1.0
        self.top = 0.5

        self.xlabel = None
        self.ylabel = None
        self.zlabel = None

        self.xspacing = 1.0
        self.yspacing = 1.0
        self.zspacing = 1.0

        self.lower = 'blue'
        self.upper = 'red'

        self.legend = None
        self.corner = 0
        self.margin = 0.2
        self.length = 0.4

        self.tick = 0.07
        self.tip = 0.1

        self.outline = False

        self.lines = []

        for name, value in more.items():
            setattr(self, name, value)

    def line(self, x=[], y=[], z=None, label=None,
            color='black', style='solid'):

        self.lines.append(locals())

    def clear(self):
        self.lines = []

    def save(self, filename):
        # determine extent of the plotting area:

        extent = {}
        extent['x'] = self.width - self.left - self.right
        extent['y'] = self.height - self.bottom - self.top

        # determine data limits:

        lower = {}
        upper = {}

        for x in 'x', 'y':
            lower[x] = min(min(line[x]) for line in self.lines if len(line[x]))
            upper[x] = max(max(line[x]) for line in self.lines if len(line[x]))

        z = [line['z'] for line in self.lines if line['z'] is not None]

        colorbar = bool(z)

        if colorbar:
            extent['z'] = extent['y']

            lower['z'] = min(z)
            upper['z'] = max(z)

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

            # choose ticks with a spacing close to the given one

            ticks[x] = [(scale[x] * (n - lower[x]), n)
                for n in multiples(lower[x], upper[x], xround_mantissa(
                    getattr(self, x + 'spacing') / scale[x]))]

        # build LaTeX file

        labels = []

        with open(filename, 'w') as file:
            # open TikZ environment

            file.write('\\begin{tikzpicture}[line cap=round]')

            # set bounding box

            file.write('\n\t\\draw [use as bounding box, %s]'
                % ('gray, very thin, dashed' if self.outline else 'draw=none'))

            file.write('\n\t\t(%.3f, %.3f) rectangle +(%.3f, %.3f);'
                % (-self.left, -self.bottom, self.width, self.height))

            # plot lines

            for line in self.lines:
                if line['z'] is not None:
                    ratio = (line['z'] - lower['z']) / (upper['z'] - lower['z'])

                    line['color'] = '%s!%.1f!%s' \
                        % (self.upper, 100 * ratio, self.lower)

                options = '%(color)s, %(style)s' % line

                if line['label'] is not None:
                    labels.append([options, line['label']])

                if len(line['x']) and len(line['y']):
                    file.write('\n\t\\draw [%s]' % options)

                    points = zip(*[[scale[x] * (n - lower[x])
                        for n in line[x]] for x in 'x', 'y'])

                    file.write('\n\t\t   ')
                    file.write('\n\t\t-- '.join('(%.3f, %.3f)'
                        % point for point in points))

                    file.write(';')

            # paint colorbar

            if colorbar:
                file.write('\n\t\\shade [bottom color=%s, top color=%s]'
                    % (self.lower, self.upper))

                file.write('\n\t\t(%.3f, 0) rectangle (%.3f, %.3f);'
                    % (extent['x'], extent['x'] + self.tip, extent['z']))

            # draw tick marks and labels

            file.write('\n\t\\draw [line cap=butt]')

            for x, label in ticks['x']:
                file.write('\n\t\t(%.3f, 0) -- +(0, %.3f) '
                    'node [below] {$%g$}' % (x, -self.tick, label))

            for y, label in ticks['y']:
                file.write('\n\t\t(0, %.3f) -- +(%.3f, 0) '
                    'node [rotate=90, above] {$%g$}' % (y, -self.tick, label))

            file.write(';')

            if colorbar:
                for z, label in ticks['z']:
                    file.write('\n\t\\node '
                        '[rotate=90, below] at (%.3f, %.3f) {$%g$};'
                        % (extent['x'] + self.tip, z, label))

            # draw coordinate axes

            file.write('\n\t\\draw [%s, line cap=butt]'
                % ('->' if colorbar else '<->'))

            file.write('\n\t\t(%.3f, 0) -- (0, 0) -- (0, %.3f);'
                % (extent['x'] + self.tip, extent['y'] + self.tip))

            # label coordinate axes

            if self.xlabel:
                file.write('\n\t\\node '
                    '[below=\\baselineskip] at (%.3f, %.3f) {%s};'
                    % (extent['x'] / 2, -self.tick, self.xlabel))

            if self.ylabel:
                file.write('\n\t\\node '
                    '[rotate=90, above=\\baselineskip] at (%.3f, %.3f) {%s};'
                    % (-self.tick, extent['y'] / 2, self.ylabel))

            if self.zlabel and colorbar:
                file.write('\n\t\\node '
                    '[rotate=90, below=\\baselineskip] at (%.3f, %.3f) {%s};'
                    % (extent['x'] + self.tip, extent['y'] / 2, self.zlabel))

            # add legend

            if labels:
                left = self.corner in {2, 3}
                down = self.corner in {3, 4}

                x, h = (0, 'right') if left else (extent['x'], 'left')
                y, v = (0, 'above') if down else (extent['y'], 'below')

                file.write('\n\t\\node '
                    '[align=center, %s %s=%.3gcm] at (%.3f, %.3f) {'
                    % (v, h, self.margin, x, y))

                if self.legend:
                    file.write('\n\t\t%s \\\\' % self.legend)

                file.write('\n\t\t\\begin{tikzpicture}'
                    '[x=%.3gcm, y=\\baselineskip]' % self.length)

                for n, (options, label) in enumerate(reversed(labels)):
                    file.write('\n\t\t\t\\draw [%s] (0, %d) -- +(1, 0) '
                        'node [right, black] {%s};' % (options, n, label))

                file.write('\n\t\t\\end{tikzpicture}')
                file.write('\n\t\t};')

            # close TikZ environment

            file.write('\n\\end{tikzpicture}\n')
