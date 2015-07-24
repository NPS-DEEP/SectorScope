DEPENDENCIES = viewer_um.tex title.tex

viewer_um.pdf: $(DEPENDENCIES)
	cd drawings; make
	pdflatex viewer_um.tex
	pdflatex viewer_um.tex

clean:
	rm -rf viewer_um.aux viewer_um.log viewer_um.out viewer_um.pdf structure.aux

