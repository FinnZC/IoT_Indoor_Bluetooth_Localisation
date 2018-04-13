all: proposal.pdf


proposal.pdf: 
	cat proposal.md | pandoc --variable fontsize=11pt --variable geometry="margin=1.5cm" -f markdown -t latex -s -o proposal.prep.tex
	latexpdf

