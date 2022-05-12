#!/usr/bin/env python3

import numpy as np
import storylines

def moebius(t, u, r=1.0):
    R = r + t * np.cos(u)

    x = R * np.cos(2 * u)
    y = R * np.sin(2 * u)
    z = t * np.sin(u)

    return zip(x, y, z)

T = np.linspace(-1.0, 1.0, 101)
U = np.linspace(0.0, np.pi, 400)

style = dict(very_thick=True, color='magenta')

objects = []

for u in U[::10]:
    objects.append((moebius(T, u), style))

for t in T[::10]:
    objects.append((moebius(t, U), style))

objects = storylines.project(objects, R=[2.0, 2.0, 2.0])

plot = storylines.Plot(xyaxes=False, height=False, margin=0.5)

for R, style in objects:
    plot.line(*list(zip(*R))[:2], **style)

plot.save('moebius', pdf=True)
