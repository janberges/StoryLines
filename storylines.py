#!/usr/bin/env python

from __future__ import division
from math import asin, atan2, ceil, cos, floor, log10, pi, sin, sqrt
import os
import re

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

def islands(N, criterion, join=False):
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
    N = len(points)

    x, y = tuple(zip(*points))

    if nib is not None:
        alpha = [nib] * (N - 1)
    else:
        alpha = [(pi / 2 + atan2(y[n + 1] - y[n], x[n + 1] - x[n]))
            % (2 * pi) for n in range(N - 1)]

    phi = alpha[:1]

    for n in range(N - 2):
        phi.append(sum(alpha[n:n + 2]) / 2)

        if max(alpha[n:n + 2]) - min(alpha[n:n + 2]) > pi:
            phi[-1] += pi

    phi.append(alpha[-1])

    X = []
    Y = []

    for sgn in 1, -1:
        for n in range(N) if sgn == 1 else reversed(range(N)):
            X.append(x[n] + cos(phi[n]) * width
                * (shifts[n] + sgn * weights[n] / 2))
            Y.append(y[n] + sin(phi[n]) * width
                * (shifts[n] + sgn * weights[n] / 2))

    return list(zip(X, Y))

def miter_butt(points, width, weights, shifts, nib=None):
    N = len(points)

    x, y = tuple(zip(*points))

    upper = []
    lower = []

    for n in range(N - 1):
        if nib is not None:
            alpha = nib
        else:
            alpha = atan2(y[n + 1] - y[n], x[n + 1] - x[n]) + pi / 2

        dx = 0.5 * width * cos(alpha)
        dy = 0.5 * width * sin(alpha)

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

def shortcut(points, search=300, search_rel=0.5):
    N = len(points)

    x, y = tuple(zip(*points))

    search = min(search, int(round(search_rel * N)))

    shortcuts = []

    dx = [x[i + 1] - x[i] for i in range(N - 1)]
    dy = [y[i + 1] - y[i] for i in range(N - 1)]

    i = 0
    while i < N - 1:
        for j in range(i + 2, min(i + search, N - 1)):
            det = dy[i] * dx[j] - dx[i] * dy[j]

            if det:
                dxij = x[j] - x[i]
                dyij = y[j] - y[i]

                u = (dx[j] * dyij - dy[j] * dxij) / det

                if 0 < u <= 1:
                    v = (dx[i] * dyij - dy[i] * dxij) / det

                    if 0 <= v < 1:
                        shortcuts.append((i, j,
                            x[i] + u * dx[i], y[i] + u * dy[i]))

                        i = j
                        break
        i += 1

    x = list(x)
    y = list(y)

    for n1, n2, x0, y0 in reversed(shortcuts):
        x[n1 + 1:n2 + 1] = [x0]
        y[n1 + 1:n2 + 1] = [y0]

    return list(zip(x, y))

def cut(points, minimum, maximum, join=False):
    points = [tuple(point) for point in points]

    n = 0 if join else 1

    while n < len(points):
        x1, y1 = points[n - 1]
        x2, y2 = points[n]

        for y in maximum, minimum:
            if y1 < y < y2 or y1 > y > y2:
                x = (x1 * (y2 - y) + x2 * (y - y1)) / (y2 - y1)
                points.insert(n, (x, y))

        n += 1

    for island in islands(len(points),
        lambda n: minimum <= points[n][1] <= maximum, join):

        yield [points[n] for n in island]

def cut2d(points, xmin, xmax, ymin, ymax, join=False):
    for group in cut(points, ymin, ymax, join):
        group = [(y, x) for x, y in group]

        for group in cut(group, xmin, xmax, join):
            group = [(x, y) for y, x in group]

            yield group

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
        for key, value in sorted(options.items())
        if value is not False)

def goto(filename):
    head, tail = os.path.split(filename)
    stem = os.path.splitext(tail)[0]

    if head:
        cwd = os.getcwd()
        os.chdir(head)

    def typeset():
        os.system('pdflatex --interaction=batchmode %s.tex' % stem)

        for suffix in 'aux', 'log':
            os.system('rm %s.%s' % (stem, suffix))

    def home():
        if head:
            os.chdir(cwd)

    return stem, typeset, home

pt = 2.54 / 72 # cm

class Plot():
    def __init__(self, width=8.0, height=6.0, margin=1.0, **more):
        self.width = width
        self.height = height

        self.flexible = False

        self.left = margin
        self.right = margin
        self.bottom = margin
        self.top = margin

        for x in 'x', 'y', 'z':
            setattr(self, x + 'label', None)
            setattr(self, x + 'ticks', None)
            setattr(self, x + 'spacing', 1.0)
            setattr(self, x + 'step', None)
            setattr(self, x + 'min', None)
            setattr(self, x + 'max', None)
            setattr(self, x + 'padding', 0.0)
            setattr(self, x + 'format',
                lambda x: ('%g' % x).replace('-', r'\llap{$-$}'))

        self.lower = 'blue'
        self.upper = 'red'

        self.title = None

        self.label = None

        self.lali = 'center'
        self.lbls = '\\baselineskip'
        self.lbox = False
        self.lcol = 1
        self.llen = '4mm'
        self.lopt = 'below left'
        self.lpos = 'lt'
        self.lrow = 0
        self.lsep = None
        self.ltop = None
        self.lwid = 4.0

        self.tick = '0.7mm'
        self.gap = 0.0
        self.tip = 0.1

        self.xyaxes = True
        self.frame = True
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

    def line(self,
            x = [],
            y = [],
            z = None,

            axes = False,
            code = None,
            cut = True,
            frame = False,
            join = None,
            label = None,
            miter = False,
            nib = None,
            omit = True,
            protrusion = 0,
            sgn = +1,
            shifts = None,
            shortcut = 0,
            thickness = 1,
            weights = None,
            xref = None,
            yref = None,
            zindex = None,

            **options):

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
            label = label,
            miter = miter,
            nib = nib,
            omit = omit,
            protrusion = protrusion,
            sgn = sgn,
            shifts = shifts,
            shortcut = shortcut,
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

    def fatband(self, x, y, weights, shifts=None, **options):
        if shifts is None:
            shifts = [0 for n in range(len(weights))]

        for island in islands(len(weights),
            lambda n: any(weights[max(n - 1, 0):n + 2])):

            if len(island) > 1:
                n = slice(island[0], island[-1] + 1)
                self.line(x[n], y[n], weights=weights[n], shifts=shifts[n],
                    **options)

    def compline(self, x, y, weights, colors, threshold=0.0, **options):
        weights = [[0 if part < threshold else part for part in parts]
            for parts in weights]

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

    def node(self, x, y, content, **options):
        self.code('\n\t\\node [%s] at (<x=%.3f>, <y=%.3f>) {%s};'
            % (csv(options), x, y, content))

    def code(self, data, **options):
        self.line(code=data, **options)

    def axes(self, **options):
        self.line(axes=True, **options)

    def clear(self):
        self.lines = []

    def save(self, filename, external=False, standalone=False, pdf=False):
        if pdf:
            standalone = True

        # interpret negative as inner dimensions:

        if self.width < 0:
            self.width = -self.width + self.left + self.right

        if self.height < 0:
            self.height = -self.height + self.bottom + self.top

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

            lower[x] -= getattr(self, x + 'padding')
            upper[x] += getattr(self, x + 'padding')

        # handle horizontal and vertical lines:

        for x, y in ('x', 'y'), ('y', 'x'):
            for line in self.lines:
                if not len(line[x]) and len(line[y]) == 1:
                    line[x] = [lower[x], upper[x]]
                    line[y] = [line[y][0]] * 2

                    line['options'].setdefault('line_cap', 'butt')

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

        stem, typeset, home = goto(filename)

        with open('%s.tex' % stem, 'w') as file:
            # print premable and open document

            if standalone:
                file.write('\\documentclass[%dpt, varwidth=\\maxdimen]{standalone}\n'
                    % self.fontsize)
                file.write('\\usepackage{tikz}\n')

                if self.preamble:
                    file.write('%s\n' % self.preamble)

                file.write('\\begin{document}\n\\noindent\n' )

            # set filename for externalization

            elif external:
                file.write('\\tikzsetnextfilename{%s}\n%%\n' % stem)

            # open TikZ environment

            if self.flexible:
                file.write('\\begingroup%%'
                    '\n\\let\\unit\\relax%%'
                    '\n\\newlength\\unit%%'
                    '\n\\setlength\\unit{%g\\linewidth}%%'
                    '\n\\begin{tikzpicture}[x=\\unit, y=\\unit, %s]'
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

            def draw_frame():
                if draw_frame.done:
                    return

                file.write('\n\t\\draw [gray, line cap=butt]'
                    '\n\t\t(%.3f, 0) -- (%.3f, %.3f) -- (0, %.3f);'
                    % tuple(extent[x] for x in 'xxyy'))

                draw_frame.done = True

            draw_frame.done = False

            def draw_axes():
                if draw_axes.done:
                    return

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

                if self.xyaxes:
                    # draw tick marks and labels

                    if ticks['x'] or ticks['y']:
                        file.write('\n\t\\draw [line cap=butt]')

                        for x, label in ticks['x']:
                            file.write('\n\t\t(%.3f, 0) -- +(0, -%s) '
                                'node [below] {%s}'
                                % (x, self.tick, label))

                        for y, label in ticks['y']:
                            file.write('\n\t\t(0, %.3f) -- +(-%s, 0) '
                                'node [rotate=90, above] {%s}'
                                % (y, self.tick, label))

                        file.write(';')

                    # draw coordinate axes

                    if self.frame:
                        draw_frame()

                    file.write('\n\t\\draw [%s, line cap=butt]'
                        % ('->' if colorbar else '<->'))

                    file.write('\n\t\t(%.3f, 0) -- (0, 0) -- (0, %.3f);'
                        % (extent['x'] + self.tip, extent['y'] + self.tip))

                # label coordinate axes

                if self.xlabel:
                    file.write('\n\t\\node [below')

                    if ticks['x']:
                        file.write('=\\baselineskip')

                    file.write('] at (%.3f, -%s)'
                        % (extent['x'] / 2, self.tick))

                    file.write('\n\t\t{%s};' % self.xlabel)

                if self.ylabel:
                    file.write('\n\t\\node [rotate=90, above')

                    if ticks['y']:
                        file.write('=\\baselineskip')

                    file.write('] at (-%s, %.3f)'
                        % (self.tick, extent['y'] / 2))

                    file.write('\n\t\t{%s};' % self.ylabel)

                if self.zlabel and colorbar:
                    file.write('\n\t\\node [rotate=90, below')

                    if ticks['z']:
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
                        line['options'][option] = ('%scm'
                            % (line['options'][option] * scale['y']))

                if line['label'] is not None:
                    labels.append([line['options'], line['label']])

                if len(line['x']) and len(line['y']):
                    for x, y in ('x', 'y'), ('y', 'x'):
                        xref = line[x + 'ref']

                        if xref is not None:
                            line[x] = list(line[x])
                            line[y] = list(line[y])

                            line[x] =      [xref] + line[x] + [xref]
                            line[y] = line[y][:1] + line[y] + line[y][-1:]

                    points = list(zip(*[[scale[x] * (n - lower[x])
                        for n in line[x]] for x in ('x', 'y')]))

                    if line['protrusion']:
                        for i, j in (1, 0), (-2, -1):
                            if line['weights'] is not None:
                                if not line['weights'][j]:
                                    continue

                            dx = points[j][0] - points[i][0]
                            dy = points[j][1] - points[i][1]
                            dr = sqrt(dx * dx + dy * dy)
                            rescale = 1 + line['protrusion'] / dr

                            points[j] = (
                                points[i][0] + dx * rescale,
                                points[i][1] + dy * rescale,
                                )

                    if line['weights'] is not None:
                        points = (miter_butt if line['miter'] else fatband)(
                            points, line['thickness'], line['weights'],
                            line['shifts'], line['nib'])

                    if line['shortcut']:
                        points = shortcut(points, line['shortcut'])

                    if line['cut']:
                        if line['join'] is None:
                            line['join'] = (line['options'].get('fill')
                                is not None)

                        if line['options'].get('only_marks'):
                            segments = [[(x, y) for x, y in points
                                if  0 <= x <= extent['x']
                                and 0 <= y <= extent['y']]]
                        else:
                            segments = cut2d(points,
                                0, extent['x'], 0, extent['y'], line['join'])
                    else:
                        segments = [points]

                    for points in segments:
                        if line['omit']:
                            points = relevant(points[::line['sgn']])

                        file.write('\n\t\\draw [%s] plot coordinates {'
                            % csv(line['options']))

                        for group in groups(points):
                            file.write('\n\t\t')
                            file.write(' '.join(form % point
                                for point in group))

                        file.write(' };')

                # insert TikZ code with special coordinates:

                if line['code']:
                    code = line['code']

                    for x in 'x', 'y':
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
                file.write('\n\t\\node at (current bounding box.north west) '
                    '[inner sep=0pt, below right] {%s};'
                    % self.label)

            # add legend

            if self.ltop is not None or labels:
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

                file.write('\n\t\\node [align=%s' % self.lali)

                if self.lopt:
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

            if self.flexible:
                file.write('\n\\endgroup%')

            # close document

            if standalone:
                file.write('\n\\end{document}')

            file.write('\n')

        # typeset document and clean up:

        if pdf:
            typeset()

        home()

def combine(filename, pdfs, columns=100, align=0.5, pdf=False):
    stem, typeset, home = goto(filename)

    with open('%s.tex' % stem, 'w') as tex:
        tex.write('\\documentclass[varwidth=\maxdimen]{standalone}\n'
            '\\usepackage{graphicx}\n'
            '\\begin{document}\n'
            '\\noindent%\n')

        for n, pdf in enumerate(pdfs, 1):
            tex.write('\\raisebox{-%g\\height}{\\includegraphics{%s.pdf}}%s\n'
                % (align, pdf, '%' if n % columns else '\\\\[-\\lineskip]'))

        tex.write('\\end{document}\n')

    if pdf:
        typeset()

    home()
