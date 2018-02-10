paws: the Platform for Automated Workflows by SSRL 
==================================================


Introduction
------------

`paws` stands for the Platform for Automated Workflows by SSRL.
It was conceived to serve as a lean and modular
workflow manager for spectral data.

`paws` interfaces fluidly
with an ever-growing number of packages 
and provide easy ways for users 
to add their own operations,
as Python modules following a simple template.

After a `paws` workflow has been constructed, 
it can be easily moved between machines, processes, or threads,
so that it can be used equally well 
for scripting on personal computers,
for processing behind graphical applications,
or for remote execution on clusters or data centers.

Disclaimer: `paws` is neither the first nor the most sophisticated
way to build and manage data processing workflows.
It was built to provide a certain degree of modularity
that was required at the time of development
but was not so easy to find in the community.

The core modules of `paws` 
are pure Python and depend only on PyYAML.

A separate package, `qtpaws`, provides a `Qt`-based GUI for `paws`.
`qtpaws` tries to provide the same functionalities as the pure Python API,
along with interactive viewing of the workflow results in real time.


Documentation
-------------

The documentation for `paws` is hosted by readthedocs.org:
`http://paws.readthedocs.io/en/latest/`.
This documentation is continually under development.
Please contact the developers at `paws-developers@slac.stanford.edu`
if the documentation fails to answer your questions.


API Examples
------------

The following are examples that explore 
the capabilities of the `paws` API.

TODO: write new examples to reflect the new API.


Installation
------------

The full `paws` package is available on PyPI.
To install in an existing Python environment, invoke `pip`:
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
TODO: add this to the docs. 


Attribution
-----------

`paws` was written at SSRL by Chris Tassone's research group.
If you use `paws` in your published research, 
a citation would be appreciated.

Before citing `paws`, it is of primary importance that you cite 
the authors of the original work that produced your results: 
this is almost certainly separate from the authors of `paws`.
Citations for your specific operations might be found
by in the `paws` documentation.
If you have trouble finding proper citations,
please contact us at `paws-developers@slac.stanford.edu`,
and we will do our best to help.


Contribution
------------

Contribution to `paws` is encouraged and appreciated.
Get in touch with the `paws` development team
at `paws-developers@slac.stanford.edu`.


License
-------

The 3-clause BSD-like license attached to this software 
can be found in the LICENSE file in the source code root directory.

