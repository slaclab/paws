#usage: sphinx-apidoc [options] -o outputdir packagedir [excluded_paths]
# -f: force overwriting of rst files
# -d: maximum TOC depth 
# --no-toc: do not generate a toc for the api
# -H [name]: package title
# -A [name]: authorship 

#sphinx-apidoc -f -d 3 -o source/apidoc_files ../paws/api/
#sphinx-apidoc -f -d 3 -o source/opdoc_files ../paws/core/operations/
sphinx-apidoc -f -d 3 -o source/packagedoc_files ../paws/ 
#../paws/core/operations/ ../paws/api/

