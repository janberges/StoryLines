#!/usr/bin/env python3

import numpy as np
import storylines

x, dx = np.linspace(-2.0, +1.0, 200, endpoint=False, retstep=True)
y, dy = np.linspace(-1.5, +1.5, 200, endpoint=False, retstep=True)

x += dx / 2
y += dy / 2

discrete = np.full((len(y), len(x)), np.nan)
smoothed = np.full((len(y), len(x)), np.nan)

for i in range(len(y)):
    for j in range(len(x)):
        z = 0
        for n in range(30):
            z = z * z + x[j] + 1j * y[i]
            r = abs(z)
            if r > 6:
                discrete[i, j] = n
                smoothed[i, j] = n - np.log2(np.log2(r))
                break

colors = storylines.colormap(
    (0, storylines.Color(0.2, 1, 255, 'PSV')),
    (1, storylines.Color(0.2 + 2 * np.pi, 1, 255, 'PSV')),
    (None, storylines.Color(0, 0, 0)))

grays = storylines.colormap(
    (0, storylines.Color(0, 0, 0)),
    (1, storylines.Color(255, 255, 255)),
    (None, storylines.Color(255, 255, 255)))

plot = storylines.Plot(xyaxes=False, height=0, xmin=0, xmax=3, ymin=0, ymax=3,
    xstep=1.0 / 6, ystep=1.0 / 6, grid=True, margin=0)

truecolor = np.round(storylines.colorize(smoothed, colors))

name = 'png_truecolor.png'
storylines.save(name, truecolor)
assert np.array_equal(truecolor, storylines.load(name))
plot.image(name, 0, 0, 1, 1)

name = 'png_truecolor_alpha.png'
alpha = np.round(storylines.colorize(smoothed, grays))[:, :, :1]
image = np.concatenate((truecolor, alpha), axis=2)
storylines.save(name, image)
assert np.array_equal(image, storylines.load(name))
plot.image(name, 1, 0, 2, 1)

name = 'png_truecolor_transparency.png'
alpha = 255 * np.any(truecolor != 0, axis=2, keepdims=True)
image = np.concatenate((truecolor, alpha), axis=2)
storylines.save(name, truecolor, trns=[0, 0, 0])
assert np.array_equal(image, storylines.load(name))
plot.image(name, 2, 0, 3, 1)

grayscale = np.round(np.average(truecolor, axis=2, keepdims=True))

name = 'png_grayscale.png'
storylines.save(name, grayscale)
assert np.array_equal(grayscale, storylines.load(name))
plot.image(name, 0, 1, 1, 2)

name = 'png_grayscale_alpha.png'
alpha = np.round(storylines.colorize(smoothed, grays))[:, :, :1]
image = np.concatenate((grayscale, alpha), axis=2)
storylines.save(name, image)
assert np.array_equal(image, storylines.load(name))
plot.image(name, 1, 1, 2, 2)

name = 'png_grayscale_transparency.png'
alpha = 255 * (grayscale != 0)
image = np.concatenate((grayscale, alpha), axis=2)
storylines.save(name, grayscale, trns=[0])
assert np.array_equal(image, storylines.load(name))
plot.image(name, 2, 1, 3, 2)

indexed = np.round(storylines.colorize(discrete, colors))

name = 'png_indexed.png'
storylines.save(name, indexed)
assert np.array_equal(indexed, storylines.load(name))
plot.image(name, 0, 2, 1, 3)

name = 'png_indexed_alpha.png'
alpha = np.round(storylines.colorize(discrete, grays))[:, :, :1]
image = np.concatenate((indexed, alpha), axis=2)
storylines.save(name, image)
assert np.array_equal(image, storylines.load(name))
plot.image(name, 1, 2, 2, 3)

name = 'png_indexed_transparency.png'
alpha = 255 * np.any(indexed != 0, axis=2, keepdims=True)
image = np.concatenate((indexed, alpha), axis=2)
storylines.save(name, indexed, trns=[0, 0, 0])
assert np.array_equal(image, storylines.load(name))
plot.image(name, 2, 2, 3, 3)

plot.save('png.png')
