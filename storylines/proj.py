#!/usr/bin/env python3

# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

import math
import re

from .calc import cross, dot

def projection(
        r=[0.0, 0.0, 0.0], # object
        R=[0.0, -1.0, 0.0], # observer
        T=[0.0, 0.0, 0.0], # target
        U=[0.0, 0.0, 1.0], # up
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

    # secant of angle of object w.r.t. viewing direction:
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
