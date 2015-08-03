DEPENDENCIES = block_match_viewer_um.tex title.tex

block_match_viewer_um.pdf: $(DEPENDENCIES)
	cd drawings; make
	pdflatex block_match_viewer_um.tex
	pdflatex block_match_viewer_um.tex

clean:
	rm -rf block_match_viewer_um.aux block_match_viewer_um.log block_match_viewer_um.out block_match_viewer_um.pdf structure.aux

