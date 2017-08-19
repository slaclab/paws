paws: the Platform for Automated Workflows by SSRL 
==================================================


Description
-----------

`paws` stands for the Platform for Automated Workflows by SSRL.
It was conceived to serve as a lean and modular 
workflow manager for image-like data.

`paws` provides machinery 
to build and execute data processing workflows,
including an ever-growing library of Operations 
that connect together to form data processing Workflows. 

The core modules of `paws` 
are pure Python and have very few dependencies.
`paws` exposes a simple API
that interacts with these core modules,
for users to write scripts based on `paws`,
or to import the `paws` API to perform
back-end computations for other applications or widgets.
The current state of `paws` is alpha-
nothing has been tested, 
and even less has been optimized.

The `paws` package also includes a graphical application 
built on the `PySide` `Qt` bindings.
Through this GUI, users can build and configure workflows, 
examine existing `paws` Operations,
develop new `paws` Operations,
and visualize the outputs of their workflows.
Various simplified GUIs are currently in development
for interacting with specific workflows. 


Example
-------

Here is an example of how to use `paws` 
to write a data processing script.
Note: at the time this was written, 
the example does not display in github.
Open the source file for this README
to see the example.
Complete instructions are included in the user manual. 
See the `doc` directory of this repository.

This script performs a common diffraction data processing workflow:
it reads some calibration parameters in PONI (PyFAI) format,
reads an image, uses the calibration parameters 
to integrate the image with PyFAI,
and windows the useful part of the data.
After executing, the useful data is extracted
and plotted using matplotlib.

TODO: update the example to reflect new API.

Installation
------------

The full `paws` package is now available on PyPI.
To install in a working Python 2.7 environment, invoke `pip`:
`pip install pypaws`

All of the dependencies of the `paws` Operations 
are not declared as dependencies of `paws`.
This keeps the Python environment relatively lean
and avoids installation overhead,
but it means that users will have to prepare their
environments for the Operations they want to use.

The documentation of `paws` includes instructions
for installing the dependencies of each Operation.
NOTE: this is currently false. 
TODO: make this be true. 

Attribution
-----------

`paws` was written at SSRL by Chris Tassone's research group.
If you use `paws` in your published research, 
we will greatly appreciate a citation. 

Before citing `paws`, it is of primary importance that you cite 
the authors of the original work that produced your results: 
this may be separate from the citation for `paws`.
Citations for your specific operations can be found
by looking those operations up in the `paws` documentation:
(TODO: insert readthedocs link here).

If the documentation is unclear for the operations you need to cite,
please contact us at `paws-developers@slac.stanford.edu`,
and we will return the correct citation
and fix the missing documentation.

A proper citation for `paws` itself can be found 
at the beginning the `paws` documentation:
(TODO: insert readthedocs link here.)


Contribution
------------

Contribution to `paws` is encouraged and appreciated.
Whether you are a researcher looking to contribute Operation wrappers to the `paws` library
or a software developer looking to contribute to the platform itself,
the `paws` development team would love to hear from you.
Get in touch with the `paws` development team
at `paws-developers@slac.stanford.edu`.

Full details about contributing to `paws`
can be found in our online documentation,
at (TODO: insert readthedocs link here).


License
-------

The 3-clause BSD-like license attached to this software 
can be found in the LICENSE file in the source code root directory.

