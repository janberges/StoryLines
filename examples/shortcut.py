#!/usr/bin/env python

import numpy as np
import storylines

N = 1000

x = np.linspace(-1, 1, N)
y = abs(x) ** 1.3
w = 1 - x ** 2

plot = storylines.Plot(margin=1, xyaxes=False)

plot.compline(x, y, w.reshape((N, 1)), colors=['yellow'], color='brown',
    thickness=1.3, cut=False, thick=True, shortcut=300)

plot.line(x, y, thick=True)

plot.save('shortcut', standalone=True, pdf=True)
