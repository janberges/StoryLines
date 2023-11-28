.PHONY: all clean

all: $(patsubst %.py, %.png, $(wildcard *.py))

clean:
	rm -f *.tex *.pdf *.png

%.png: %.py
	python3 $^
