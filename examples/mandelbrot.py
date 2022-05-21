#!/usr/bin/env python3

import numpy as np
import storylines

w = h = 300
N = 30

xmin = -2.1
xmax = +0.9
ymin = -1.5
ymax = +1.5

x, dx = np.linspace(xmin, xmax, w, endpoint=False, retstep=True)
y, dy = np.linspace(ymin, ymax, h, endpoint=False, retstep=True)

x += dx / 2
y += dy / 2

image = np.empty((h, w))

for i in range(h):
    for j in range(w):
        z = 0
        for n in range(N):
            z = z * z + x[j] + 1j * y[i]
            r = abs(z)
            if r > 6:
                image[i, j] = n - np.log2(np.log(r))
                break
        else:
            image[i, j] = np.nan

phase0 = 0.2
phase1 = phase0 + 2 * np.pi

cmap = storylines.colormap(
    (0, storylines.Color(phase0, 1, 255, 'PSV')),
    (1, storylines.Color(phase1, 1, 255, 'PSV')),
    (None, storylines.Color(0, 0, 0)))

plot = storylines.Plot(height=0.0, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
    zmin=np.nanmin(image), zmax=np.nanmax(image), cmap=cmap, frame=False,
    title='Mandelbrot set', xlabel='Re', ylabel='Im', zlabel='Iterations',
    background='mandelbrot.bg.png')

storylines.save(plot.background, storylines.colorize(image, cmap))

plot.save('mandelbrot.png')
