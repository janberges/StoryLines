#!/usr/bin/env python

import numpy as np
import storylines

plot = storylines.Plot(lpos='rb', lopt='above left')

t = np.linspace(-1, 1, 100)

for omega in np.linspace(0, np.pi, 10):
    plot.line(t, np.sin(omega * t), omega, mark='*')

plot.xlabel = '$t / \mathrm s$'
plot.ylabel = '$\sin(\omega t)$'
plot.zlabel = '$\omega / \mathrm{s^{-1}}$'

plot.line(label='polygonal path')
plot.line(label='relevant points', mark='*', only_marks=True)

plot.save('example.tex', standalone=True)
