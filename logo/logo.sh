#!/bin/bash

w=32
h=17
in=2.54

pdflatex --interaction=batchmode StoryLines

convert -density `perl -e "print 640 / ($w / $in)"` StoryLines.pdf \
    -flatten PNG8:StoryLines.png

convert -density `perl -e "print 640 / ($w / $in)"` StoryLines.pdf \
    -background white -gravity center -extent 640x640 PNG8:StoryLines_square.png

convert -density `perl -e "print 480 / ($h / $in)"` StoryLines.pdf \
    -background white -gravity center -extent 1280x640 PNG8:StoryLines_banner.png
