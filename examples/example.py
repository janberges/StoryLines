#!/usr/bin/env python3

import numpy as np
import storylines

cmap = storylines.colormap(
    (0, storylines.Color(240, 1, 255, 'HSV')),
    (1, storylines.Color(0, 1, 255, 'HSV')))

plot = storylines.Plot(lpos='rb', lopt='above left', cmap=cmap)

t = np.linspace(-1.0, 1.0, 100)

for omega in np.linspace(0.0, np.pi, 10):
    plot.line(t, np.sin(omega * t), omega, mark='*', omit=True)

plot.title = 'StoryLines'
plot.xlabel = '$t / \\mathrm s$'
plot.ylabel = '$\\sin(\\omega t)$'
plot.zlabel = '$\\omega / \\mathrm{s^{-1}}$'

plot.line(label='relevant points', mark='*', only_marks=True)

plot.save('example.png')
