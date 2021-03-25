#!/usr/bin/env python3

import numpy as np
import storylines

plot = storylines.Plot(lpos='rb', lopt='above left')
plot.axes()

t = np.linspace(-1.0, 1.0, 100)

for omega in np.linspace(0.0, np.pi, 10):
    plot.line(t, np.sin(omega * t), omega, mark='*')

plot.title = 'StoryLines'
plot.xlabel = '$t / \mathrm s$'
plot.ylabel = '$\sin(\omega t)$'
plot.zlabel = '$\omega / \mathrm{s^{-1}}$'

plot.line(label='relevant points', mark='*', only_marks=True)

plot.save('example', standalone=True, pdf=True)
