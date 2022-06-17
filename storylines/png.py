# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Save and load RGB(A) graphics."""

from __future__ import division

import zlib, struct

def save(filename, image):
    """Save grayscale, RGB, or RGBA image as 8-bit PNG.

    Specified at https://www.w3.org/TR/PNG/.
    Inspired by Blender thumbnailer code.

    Parameters
    ----------
    filename : str
        Name of PNG file to be written.
    image : list of list of list
        8-bit image data of shape (height, width, colors), where colors may be
        1 (grayscale), 3 (RGB), or 4 (RGBA).
    """
    height = len(image)
    width = len(image[0])
    colors = len(image[0][0])

    color = {1: 0, 3: 2, 4: 6}[colors]

    byte = [min(max(int(round(x)), 0), 255)
        for row in image
        for col in [[0]] + list(row)
        for x in col]

    # 0 before each row: https://www.w3.org/TR/PNG/#4Concepts.EncodingFiltering

    with open(filename, 'wb') as png:
        png.write(b'\x89PNG\r\n\x1a\n')

        def chunk(name, data):
            png.write(struct.pack('!I', len(data)))
            png.write(name)
            png.write(data)
            png.write(struct.pack('!I', zlib.crc32(name + data) & 0xffffffff))

        chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, color, 0, 0, 0))
        chunk(b'IDAT',
            zlib.compress(struct.pack('%dB' % len(byte), *byte), 9))
        chunk(b'IEND', b'')

def load(filename):
    """Load grayscale, RGB, or RGBA image from 8-bit PNG.

    Parameters
    ----------
    filename : str
        Name of PNG file to be written.

    Returns
    -------
    list of list of list
        8-bit image data of shape (height, width, colors), where colors may be
        1 (grayscale), 3 (RGB), or 4 (RGBA).
    """
    with open(filename, 'rb') as png:
        png.read(8)

        while True:
            size, = struct.unpack('!I', png.read(4))
            name = png.read(4)
            data = png.read(size)
            csum = png.read(4)

            if struct.pack('!I', zlib.crc32(name + data) & 0xffffffff) != csum:
                print("Chunk '%s' corrupted!" % name)

            if name == b'IHDR':
                width, height, _, color, _, _, _ = struct.unpack('!2I5B', data)
                colors = {0: 1, 2: 3, 6: 4}[color]

            elif name == b'IDAT':
                data = zlib.decompress(data)
                byte = struct.unpack('%dB' % len(data), data)

                image = [[[byte[y * (width * colors + 1) + 1 + x * colors + z]
                    for z in range(colors)]
                    for x in range(width)]
                    for y in range(height)]

            if name == b'IEND':
                break

        return image
