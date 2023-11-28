.PHONY: all clean

w = 32
h = 17
in = 2.54

all: StoryLines.png StoryLines_square.png StoryLines_banner.png

%.pdf: %.tex
	pdflatex --interaction=batchmode $*

StoryLines.png: StoryLines.pdf
	convert -density `perl -e "print 640 / ($(w) / $(in))"` $< \
        -flatten PNG8:$@

StoryLines_square.png: StoryLines.pdf
	convert -density `perl -e "print 640 / ($(w) / $(in))"` $< \
        -gravity center -extent 640x640 PNG8:$@

StoryLines_banner.png: StoryLines.pdf
	convert -density `perl -e "print 480 / ($(h) / $(in))"` $< \
        -gravity center -extent 1280x640 PNG8:$@

clean:
	rm -f *.aux *.log *.pdf *.png
