# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Inches to centimeters etc."""

from __future__ import division

inch = 2.54
"""Inch in centimeters."""

pt = inch / 72.27
"""LaTeX point in centimeters."""

def csv(options, context=' [%s]'):
    """Format TikZ options.

    Parameters
    ----------
    options : dict
        TikZ options, where spaces in keys are represented by underscores.
    context : str
        Format string with context applied to results of nonzero length only.

    Returns
    -------
    str
        Comma-separated key-value pairs in TikZ format (with `context`).
    """
    result = ', '.join(key.replace('_', ' ')
        + ('' if value is True else '=%s' % value)
        for key, value in sorted(options.items())
        if value is not False and value is not None)

    if context and result:
        return context % result
    else:
        return result
