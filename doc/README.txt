How to build paws docs:

(0) If modules have been removed or renamed, execute from this directory:
rm -rf ./source/moduledoc_files/

(1) From this directory:
./build_scripts/build_rst_files.x
Note: open this script and change the arguments 
to control which modules do or do not get rst files generated.

(2) From this directory:
./build_scripts/build_html.x

(3) From this directory:
./build_scripts/build_tex.x

