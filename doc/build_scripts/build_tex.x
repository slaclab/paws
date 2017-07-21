sphinx-build -c source -b latex source tex
cd tex
pdflatex paws.tex
pdflatex paws.tex
mv paws.pdf ../manual.pdf
