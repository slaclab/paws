#usage: sphinx-apidoc [options] -o outputdir packagedir [excluded_paths]
# -f: force overwriting of rst files
# --no-toc: do not generate a toc for the api
# -H [name]: package title
# -A [name]: authorship 

sphinx-apidoc -f --no-toc -H paws.api -A '2017 Lenson A. Pellouchoud' -o source/apidoc_files ../paws ../paws/ui/ ../paws/core/ 

sphinx-apidoc -f --no-toc -H paws -A '2017 Lenson A. Pellouchoud' -o source/moduledoc_files ../paws ../paws/api/

