#!/usr/bin/env python3

import storylines

plot = storylines.Plot(xyaxes=False, width=8, height=3, margin=0,
    lcol=4, lwid=6, preamble='\\selectcolormodel{natural}')

for name, color in storylines.color.items():
    plot.line(mark='square*', mark_size='1mm', line_width='1mm',
        fill=name, draw=color, only_marks=True, label=name)

plot.save('colors.png')
