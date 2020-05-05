#!/usr/bin/env python

import numpy as np
import storylines

N = 301

x = np.linspace(-np.pi, np.pi, N)
y = np.cos(x)

w = np.empty((N, 2))
w[:, 0] = np.cos(5 * x) ** 2 / 2
w[:, 1] = np.sin(5 * x) ** 2 / 2

plot = storylines.Plot(xyaxes=False, margin=0.5)

plot.compline(x, y, w, colors=['red', 'green'], draw='none')

plot.save('fatband', standalone=True, pdf=True)
