.PHONY: example clean

example:
	python example.py
	pdflatex -shell-escape example.tex

clean:
	rm -f *.aux *.auxlock *.dpth *.log .*.lb *.md5 *.pyc *.synctex.gz
