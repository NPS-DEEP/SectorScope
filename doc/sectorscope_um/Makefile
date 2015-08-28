DEPENDENCIES = sectorscope_um.tex title.tex

sectorscope_um.pdf: $(DEPENDENCIES)
	cd drawings; make
	pdflatex sectorscope_um.tex
	pdflatex sectorscope_um.tex

clean:
	rm -rf sectorscope_um.aux sectorscope_um.log sectorscope_um.out sectorscope_um.pdf structure.aux

