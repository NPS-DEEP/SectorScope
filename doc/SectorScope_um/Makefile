DEPENDENCIES = SectorScope_um.tex title.tex

SectorScope_um.pdf: $(DEPENDENCIES)
	cd drawings; make
	pdflatex SectorScope_um.tex
	pdflatex SectorScope_um.tex

clean:
	rm -rf SectorScope_um.aux SectorScope_um.log SectorScope_um.out SectorScope_um.pdf structure.aux

