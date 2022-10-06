# Copyright (C) 2016-2022 Jan Berges
# This program is free software under the terms of the BSD Zero Clause License.

"""Typeset TeX, rasterize PDF."""

from __future__ import division

import os
import subprocess

def goto(filename):
    """Go to output directory for plot typesetting.

    Parameters
    ----------
    filename : str
        LaTeX file name including possible path.

    Returns
    -------
    stem : str
        File name without path and extension.
    typ : str
        Desired file type (extension).
    home : function
        Function to return to previous working directory.
    """
    head, tail = os.path.split(filename)

    for extension in 'tex', 'pdf', 'png':
        if tail.endswith('.%s' % extension):
            stem = tail[:-len(extension) - 1]
            typ = extension
            break
    else:
        stem = tail
        typ = None

    if head:
        cwd = os.getcwd()
        subprocess.call(['mkdir', '-p', head])
        os.chdir(head)

    def home():
        if head:
            os.chdir(cwd)

    return stem, typ, home

def typeset(stem):
    """Run ``pdflatex`` and remove ``.aux`` and ``.log`` files.

    Parameters
    ----------
    stem : str
        File name without path and extension (in current working directory).
    """
    try:
        subprocess.call(['pdflatex', '--interaction=batchmode',
            '%s.tex' % stem])

        for suffix in 'aux', 'log':
            os.remove('%s.%s' % (stem, suffix))

    except OSError:
        print('pdflatex not found')

def rasterize(stem, dpi=300.0, width=0, height=0):
    """Run ``pdftoppm`` and remove ``-1`` from name of resulting PNG file.

    Parameters
    ----------
    stem : str
        File name without path and extension (in current working directory).
    dpi : float, default 300.0
        Image resolution in dots per inch.
    width, height : int
        Image dimensions in pixels. If either `width` or `height` is zero, it
        will be determined by the aspect ratio of the image. If both are zero,
        they will also be determined by `dpi`.
    """
    try:
        args = ['-png']

        if width or height:
            args += ['-scale-to-x', '%g' % (width or -1)]
            args += ['-scale-to-y', '%g' % (height or -1)]
        else:
            args += ['-r', '%g' % dpi]

        subprocess.call(['pdftoppm'] + args + ['%s.pdf' % stem, stem])

        os.rename('%s-1.png' % stem, '%s.png' % stem)

    except OSError:
        print('pdftoppm not found')

def combine(filename, pdfs, columns=100, align=0.5, halign='left', pdf=False,
        png=False, dpi=300.0):
    """Arrange multiple PDFs in single file.

    Parameters
    ----------
    filename : str
        Name of combined file.
    pdfs : list of str
        Names of PDFs to be combined.
    columns : int, default 100
        Number of PDFs to be arranged side by side.
    align : float, default 0.5
        Vertical alignment of PDFs, where 0, 0.5, and 1 stand for the bottom,
        center, and top of the individual figures.
    halign : str, default 'left'
        Horizontal alignment of PDFs. Possible values are ``'left'``,
        ``'center'`` and ``'right'``.
    pdf : bool, default False
        Convert resulting TeX file to PDF? Automatically set to ``True`` if
        `filename` ends with ``.pdf``.
    png : bool, default False
        Convert resulting PDF file to PNG? This implies `pdf`. Automatically set
        to ``True`` if `filename` ends with ``.png``.
    dpi : float, default 300.0
        Image resolution in dots per inch.
    """
    stem, typ, home = goto(filename)

    png = png or typ == 'png'
    pdf = pdf or typ == 'pdf' or png

    with open('%s.tex' % stem, 'w') as tex:
        tex.write('\\documentclass[varwidth=1189mm]{standalone}\n'
            '\\usepackage{graphicx}\n'
            '\\begin{document}\n'
            '\\noindent%\n')

        if halign == 'center':
            tex.write('\\centering%\n')
        elif halign == 'right':
            tex.write('\\raggedleft%\n')

        for n in range(len(pdfs)):
            nobreak = (n + 1) % columns or n + 1 == len(pdfs)
            tex.write('\\raisebox{-%g\\height}{\\includegraphics{{%s}.pdf}}%s\n'
                % (align, pdfs[n], '%' if nobreak else '\\\\[-\\lineskip]'))

        tex.write('\\end{document}\n')

    if pdf:
        typeset(stem)

    if png:
        rasterize(stem, dpi)

    home()
