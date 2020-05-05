#!/usr/bin/env python

import numpy as np
import storylines

x = np.linspace(-np.pi / 2, np.pi / 2, 101)
y = x ** 2
z = 0.5 * np.cos(x) ** 2

plot = storylines.Plot(xyaxes=False, margin=0.1)

plot.line(x, y, weights=z, shifts=z / 2, draw='none', fill='blue')

plot.save('fatband', standalone=True, pdf=True)
