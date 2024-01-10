#!/usr/bin/env python3

import numpy as np
import storylines
import sys

white = np.array([0xff, 0xff, 0xff])
red = np.array([0xff, 0x00, 0x00])

N = 11

shade = np.linspace(white, red, N)

image = np.array(storylines.load(sys.argv[1]))[:, :, :3]

for y in range(image.shape[0]):
    for x in range(image.shape[1]):
        image[y, x] = min(shade, key=lambda c: np.linalg.norm(c - image[y, x]))

storylines.save(sys.argv[2], image)
