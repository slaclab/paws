# 1)
# this conda build was started by:
# > conda skeleton pypi pypaws

# 2)
# the resulting meta.yaml, build.sh, build.bat files
# were then moved into this directory

# 3)
# pyside and qdarkstyle were then added to meta.yaml,
# under requirements.run,
# so that the build would pass import tests

# 4)
# if this is the first build on the machine, 
# make a fresh conda environment
# > <conda2_bin_path>/conda create -n paws_py2 python 

# 5)
# the paws_py2 conda virtual environment must be activated
# > source <conda2_bin_path>/activate paws_py2 

# 6)
# invoke conda-build 
# > <conda2_bin_path>/conda-build conda-build/
# NOTE: the path to the new conda package
# is found at the end of the conda-build output

# 7)
# make a free account on anaconda.org.
# install the anaconda client if it isn't already installed.
# > <conda2_bin_path>/conda install anaconda-client

# 8) 
# log in using the anaconda client:
# note that the anaconda binary is part of anaconda3
# > <anaconda3_bin_path>/anaconda login

# 9)
# use the client to upload the package.


