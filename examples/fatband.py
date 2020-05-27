#!/usr/bin/env python

import numpy as np
import storylines

N = 301

x = np.linspace(-np.pi, np.pi, N)
y = np.cos(x)

w = np.empty((N, 2))
w[:, 0] = np.maximum(0, np.cos(5 * x) ** 3) / 2
w[:, 1] = np.maximum(0, np.sin(5 * x) ** 3) / 2

plot = storylines.Plot(margin=0.5)

plot.compline(x, y, w, colors=['red', 'green'], draw='none', cut=True)

plot.save('fatband', standalone=True, pdf=True)
