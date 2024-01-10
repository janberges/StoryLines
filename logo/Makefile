.PHONY: all clean

all: StoryLines.pdf StoryLines.png StoryLines_square.png StoryLines_banner.png

%.pdf: %.tex
	pdflatex --interaction=batchmode $*

StoryLines.png: StoryLines.svg
	inkscape -w 480 -b white -o $@ $<
	python3 optimize.py $@ $@

StoryLines_square.png: StoryLines.png
	convert $< -gravity center -extent 480x480 $@

StoryLines_banner.png: StoryLines.png
	convert $< -gravity center -extent 1280x640 $@

clean:
	rm -f *.aux *.log *.pdf *_*.png
