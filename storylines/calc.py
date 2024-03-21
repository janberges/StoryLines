# Copyright (C) 2016-2024 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Mathematical helpers."""

from __future__ import division

import math

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

def multiply(A, b):
    """Multiply vector by scalar.

    Parameters
    ----------
    A : list of float
        Vector.
    b : float
        Scalar.

    Returns
    -------
    list of float
        `A` multiplied by `b`.
    """
    return [a * b for a in A]

def divide(A, b):
    """Divide vector by scalar.

    Parameters
    ----------
    A : list of float
        Vector.
    b : float
        Scalar.

    Returns
    -------
    list of float
        `A` divided by `b`.
    """
    return [a / b for a in A]

def add(A, B):
    """Calculate sum of two vectors.

    Parameters
    ----------
    A, B : list of float
        Vectors to be added.

    Returns
    -------
    list of float
        Sum of `A` and `B`.
    """
    return [a + b for a, b in zip(A, B)]

def subtract(A, B):
    """Calculate difference of two vectors.

    Parameters
    ----------
    A, B : list of float
        Vectors to be subtracted.

    Returns
    -------
    list of float
        Difference of `A` and `B`.
    """
    return [a - b for a, b in zip(A, B)]

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
    list of float
        Cross product of `A` and `B`.
    """
    return [
        A[1] * B[2] - A[2] * B[1],
        A[2] * B[0] - A[0] * B[2],
        A[0] * B[1] - A[1] * B[0],
        ]

def length(A):
    """Calculate length of vector.

    Parameters
    ----------
    A : list of float
        Vector.

    Returns
    -------
    float
        Length of `A`.
    """
    return math.sqrt(dot(A, A))

def distance(A, B):
    """Calculate distance of two vectors.

    Parameters
    ----------
    A, B : list of float
        Vectors.

    Returns
    -------
    float
        Distance of `A` and `B`.
    """
    return length(subtract(A, B))

def bonds(R1, R2=None, d1=0.0, d2=None, dmin=0.1, dmax=5.0):
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

    if R2 is None:
        R2 = R1

    if d2 is None:
        d2 = d1

    oneway = R2 is R1

    for n, r1 in enumerate(R1):
        for m, r2 in enumerate(R2):
            if oneway and m <= n:
                continue

            d = distance(r1, r2)

            if dmin < d < dmax:
                s1 = d1 / d
                s2 = d2 / d

                bonds.append([
                    [(1 - s1) * a + s1 * b for a, b in zip(r1, r2)],
                    [s2 * a + (1 - s2) * b for a, b in zip(r1, r2)],
                    ])

    return bonds

def faces(R, d=0.0, dmin=0.1, dmax=5.0, nc=10):
    """Find triangular faces, e.g., of tetrahedra of atoms.

    Parameters
    ----------
    R : list of tuple
        (Ordered) set of points.
    d : float
        Shortening at the corners, e.g., atomic radius.
    dmin, dmax : float
        Minimum and maximum side length.
    nc : int
        Number of points to trace path around corners.

    Returns
    -------
    list of list of tuple
        Outlines of faces.
    """
    faces = []

    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            if not dmin < distance(R[i], R[j]) < dmax:
                continue

            for k in range(j + 1, len(R)):
                if not dmin < distance(R[j], R[k]) < dmax:
                    continue

                if not dmin < distance(R[k], R[i]) < dmax:
                    continue

                if not d or nc < 1:
                    face = [R[i], R[j], R[k]]
                else:
                    face = []

                    for I, J, K in (i, j, k), (j, k, i), (k, i, j):
                        for n in range(nc + 1):
                            D = [(rj * n + rk * (nc - n)) / nc - ri
                                for ri, rj, rk in zip(R[I], R[J], R[K])]
                            face.append(add(R[I], multiply(D, d / length(D))))

                face.append(face[0])
                faces.append(face)

    return faces

def spring(r1, r2, N=500, k=50, radius=0.1, ends=0.15, xscale=1.0, yscale=1.0):
    """Draw coil spring in three-dimensional space.

    Parameters
    ----------
    r1, r2 : list of float
        End points.
    N : int
        Number of path segments.
    k : float
        Winding wave vector.
    radius : float
        Radius of spring.
    ends : float
        Taper length on both ends.
    scalex, scaley : float, default 1.0
        Scaling factors in transverse directions. If only one of these is zero,
        the coil becomes a flat wavy line.

    Returns
    -------
    list of list of float
        Coordinates of spring.
    """
    z = subtract(r2, r1)
    z = divide(z, length(z))
    x = cross([0, 1, 0] if z[0] or z[2] else [1, 0, 0], z)
    x = divide(x, length(x))
    y = cross(z, x)

    path = []

    for n in range(N + 1):
        r = divide(add(multiply(r1, N - n), multiply(r2, n)), N)

        d1 = distance(r, r1)
        d2 = distance(r, r2)

        envelope = radius

        if d1 < ends:
            envelope *= (1 - math.cos(d1 * math.pi / ends)) / 2

        if d2 < ends:
            envelope *= (1 - math.cos(d2 * math.pi / ends)) / 2

        r = add(r, multiply(x, xscale * envelope * math.cos(k * d1)))
        r = add(r, multiply(y, yscale * envelope * math.sin(k * d1)))

        path.append(r)

    return path
