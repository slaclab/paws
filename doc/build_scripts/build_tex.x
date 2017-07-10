sphinx-build -c `pwd` -b latex source tex
cd tex
pdflatex paws.tex
mv paws.pdf ../manual.pdf
