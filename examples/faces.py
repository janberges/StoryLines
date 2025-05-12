#!/usr/bin/env python3

import storylines
import math

corners = [
    [-0.5, 0.0, 0.0],
    [0.5, 0.0, 0.0],
    [0.0, 0.5 * math.sqrt(3), 0.0],
    [0.0, 0.5 / math.sqrt(3), math.sqrt(2) / math.sqrt(3)]
]

objects = [(bond, dict())
    for bond in storylines.faces(R=corners, d=0.2, dmin=0.9, dmax=1.1)]

plot = storylines.Plot(xyaxes=False, height=0.0, margin=0.5)

for (R, style), cosine in zip(*storylines.project(objects, R=[1, 1, 5],
    return_cosines=True)):

    plot.line(*list(zip(*R))[:2], fill='cyan!%g!blue' % (100 * cosine),
        opacity=0.3)

plot.save('faces.png')
