#!/usr/bin/env python

import numpy as np
import storylines

N = 1000

x = np.linspace(-1, 1, N)
y = abs(x) ** 1.3
w = 1 - x ** 2

plot = storylines.Plot(margin=1, xyaxes=False)

settings = dict(thickness=1.3, thick=True)

for fill, color, shortcut in ('yellow', 'gray', 0), ('none', 'black', 1):
    plot.compline(x, y, w.reshape((N, 1)),
        colors=[fill], draw=color, shortcut=shortcut, **settings)

for fill, miter in ('brown', True), ('yellow', False):
    plot.compline([-0.5, 0, 0.5], [0.8, 1.3, 0.8], [[0.5]] * 3,
        colors=[fill], draw='black', miter=miter, **settings)

plot.line(
    [-0.2, -0.1, 0.0, 0.1, 0.2, 0.1, 0.0, -0.1, -0.2],
    [ 0.7,  0.8, 0.7, 0.6, 0.7, 0.8, 0.7,  0.6,  0.7],
    shortcut=100, shortcut_rel=1)

plot.line(
    [-0.2, -0.1, 0.0, 0.1, 0.2, 0.1, 0.0, -0.1, -0.2],
    [ 0.5,  0.6, 0.5, 0.6, 0.5, 0.4, 0.5,  0.4,  0.5],
    shortcut=100, shortcut_rel=1)

plot.line(x, y, draw='brown', thick=True)

plot.save('shortcut', standalone=True, pdf=True)
