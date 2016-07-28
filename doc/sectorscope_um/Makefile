# Note: example LaTex environment: FC22 with packages:
# texlive-latex, texlive-latex-bin, 
# texlive-collection-fontsrecommended
# texlive-todonotes
# texlive-placeins
# texlive-babel-english
# texlive-amscls
# texlive-catoptions
# texlive-appendix
# texlive-fancyhdr

DEPENDENCIES = sectorscope_um.tex title.tex screenshots/*

sectorscope_um.pdf: $(DEPENDENCIES)
	pdflatex sectorscope_um.tex
	pdflatex sectorscope_um.tex

clean:
	rm -rf sectorscope_um.aux sectorscope_um.log sectorscope_um.out sectorscope_um.pdf structure.aux

