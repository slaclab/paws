# 1)
# start the build using the lates PyPI version: 
# > conda skeleton pypi pypaws

# 2)
# move the resulting pypaws/meta.yaml 
# to this directory (conda-build/meta.yaml) 

# 3)
# if this is the first build on the machine, 
# make a fresh conda environment
# > conda create -n paws python 
# ... then activate the environment
# > source activate paws 

# 4)
# invoke conda-build 
# > conda-build conda-build/
# NOTE: the path to the new conda package is at the end of the build,
# on the line marked "TEST END: <path-to-package>"

# 5)
# make a free account on anaconda.org.
# install the anaconda client if it isn't already installed.
# > conda install anaconda-client

# 6) 
# log in using the anaconda client:
# > anaconda login

# 7)
# use the client to upload the package
# (see step 4 above for package path):
# > anaconda upload <path-to-package> 


