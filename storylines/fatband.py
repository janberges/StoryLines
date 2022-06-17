# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Plot weights along line."""

from __future__ import division

import math

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
