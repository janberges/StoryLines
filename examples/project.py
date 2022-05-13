#!/usr/bin/env python3

import storylines

atoms = [(x, y, z)
    for x in range(2)
    for y in range(2)
    for z in range(2)]

observer = [1.7, 2.0, 2.3]

radius = 0.1

ball = dict(mark='ball', ball_color='purple', mark_size=radius,
    only_marks=True, omit=False)

spring = dict(line_width=0.01, color='gray', decorate=True,
    decoration='{coil, pre length=<0.05>cm, post length=<0.05>cm, '
        'segment length=<0.05>cm, amplitude=<0.05>cm}')

bonds = storylines.bonds(R1=atoms, R2=atoms,
    d1=radius, d2=radius, dmin=0.9, dmax=1.1)

objects = []

for atom in atoms:
    objects.append(([atom], ball))

for bond in bonds:
    objects.append((bond, spring))

objects = storylines.project(objects, R=observer)

plot = storylines.Plot(preamble=r'\usetikzlibrary{decorations.pathmorphing}',
    xyaxes=False, height=0.0, margin=1.0)

for R, style in objects:
    plot.line(*list(zip(*R))[:2], **style)

plot.save('project.pdf')
