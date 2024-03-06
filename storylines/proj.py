# Copyright (C) 2016-2024 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Project 3D object onto plane."""

from __future__ import division

import re

from .calc import divide, subtract, cross, dot, length, distance

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
    Z = subtract(T, R)
    Z = divide(Z, length(Z))

    # horizontal screen direction:
    X = cross(Z, U)
    X = divide(X, length(X))

    # vertical screen direction:
    Y = cross(X, Z)

    # observer-object distance vector:
    D = subtract(r, R)

    # observer-object distance (hypotenuse):
    hyp = length(D)

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

def project(objects, by_distance=True, return_cosines=False, return_order=False,
        R=[0.0, -1.0, 0.0], *args, **kwargs):
    """Project list of 3D objects onto 2D screen.

    Line width, mark sizes, and length in angle brackets are scaled according
    to the distance from the observer.

    Parameters
    ----------
    objects : list of tuple
        List of objects. Each object is represented by a tuple, which consists
        of a list of three-tuples ``(x, y, z)`` and a style dictionary.
    by_distance : bool, default True
        Sort the objects by distance so that close object overlay remote
        objects?
    return_cosines : bool, default False
        Calculate cosines of angles between objects and viewing direction?
    return_order : bool, default False
        Also return sorting order as list of indices?
    R : list of float, optional
        Observer position.

    *args, **kwargs
        Arguments passed to `projection`.

    Returns
    -------
    list of tuple
        Objects in same format, but sorted with transformed coordinates and
        adjusted styles.
    list of float, optional
        Cosines of angles between objects and viewing direction.
    list of int, optional
        Sorting order.
    """
    if by_distance:
        distances = [distance(R, [sum(x) / len(x) for x in zip(*coordinates)])
            for coordinates, style in objects]

    if return_cosines:
        cosines = []

        for coordinates, style in objects:
            view = subtract(R, [sum(x) / len(x) for x in zip(*coordinates)])

            if len(coordinates) < 2:
                normal = view
            elif len(coordinates) == 2:
                normal = cross(subtract(coordinates[1], coordinates[0]),
                    cross(subtract(coordinates[1], coordinates[0]), view))
            else:
                normal = cross(subtract(coordinates[1], coordinates[0]),
                    subtract(coordinates[2], coordinates[0]))

            cosines.append(abs(dot(normal, view))
                / (length(normal) * length(view)))

    objects = [([projection(coordinate, R=R, *args, **kwargs)
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
                style[option] = re.sub('(?<=<)([\\d.]+)(?=>)', lambda match:
                    '%.3f' % (float(match.group(1)) * zoom[n]), style[option])

    if by_distance:
        order = sorted(range(len(distances)), key=lambda n: -distances[n])
        objects = [objects[n] for n in order]

        if return_order:
            if return_cosines:
                return objects, cosines, order

            return objects, order

    if return_cosines:
        return objects, cosines

    return objects
