.PHONY: html png clean

html: png
	sphinx-build -M html . .

png:
	$(MAKE) -C ../examples/

clean:
	rm -rf doctrees html
