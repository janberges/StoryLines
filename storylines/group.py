# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Chunk sequences of points."""

from __future__ import division

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
