# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Remove redundant or unwanted points."""

from __future__ import division

import math

from .group import islands

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
