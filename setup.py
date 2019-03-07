"""
paws setup module
---- ----- ------
from https://packaging.python.org/distributing/
"""

#from setuptools import setup, find_packages
# To use a consistent encoding
#from codecs import open

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here,'README.rst')) as f:
    long_description = f.read()

# Get authorship as string from contributors.txt
__authorship__=''
with open(path.join(here,'contributors.txt')) as f: 
    for line in f.readlines():
        __authorship__ += line.strip()+', '
__authorship__ = __authorship__[:-2]

# Executing paws/config.py defines __version__ 
with open(path.join(here,'paws','config.py')) as f: 
    exec(f.read())

setup(
    name='pypaws',
    version=__version__,
    description='the Platform for Automated Workflows by SSRL',
    long_description=long_description,
    url='https://github.com/slaclab/paws/',
    author=__authorship__,
    author_email='paws-developers@slac.stanford.edu',
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='data analysis workflow',

    packages=find_packages(exclude=[]),
    #py_modules=["my_module"],

    package_dir={'paws':'paws'},

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[\
        'pyyaml','numpy','scipy',\
        'fabio','pyfai','xrsdkit',\
        'tzlocal','pyserial','paramiko',\
        'pypif','citrination_client'\
        ],
    python_requires='>=2.7',

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data = True,
    package_data={
        '': ['contributors.txt'],
        #'': ['contributors.txt','all_requirements.txt'],
        #'': ['all_requirements.txt'],
        #'paws': ['qt/graphics/*.png','qt/qtui/*.ui'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. 
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('', ['contributors.txt'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        #'paws=main:main',
    #        # TODO: add a jupyter/ipython console entry point 
    #        #'pawsconsole=paws.qt.widgets.widget_launcher:ipypaws',
    #    ],
    #},
)
