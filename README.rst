paws: the Platform for Automated Workflows by SSRL 
==================================================


Introduction
------------

`paws` stands for the Platform for Automated Workflows by SSRL.
It was conceived to serve as a lean and modular
workflow manager for image-like data.
While there are many Python packages 
providing for a wide variety of processing tasks,
we are often faced with a need to bring several packages together,
and then to add some home-built scripts as well, 
to complete a data processing workflow.
`paws` was designed to make this process easy,
by providing interfaces to an ever-growing number of existing packages 
and providing easy ways for users to add their own operations.
Occasionally, we have need of an operation 
that is not provided by a Python package that we know of.
In these rare cases, we have developed original operations within PAWS,
but such operations intend to live in a lower-level package
as soon as they are mature.

After a `paws` workflow has been constructed, 
it can be easily moved between machines, processes, or threads,
so that it can be used equally well 
for scripting or data processing on personal computers,
for data processing behind other graphical applications,
or for remote execution on clusters or data centers.
`paws` is currently under development: 
nothing has been tested or optimized.

Disclaimer: `paws` is neither the first nor the most sophisticated
way to build and manage data processing workflows.
It is, however, very modular and extensive.
It was built to serve equally well as a pure Python package,
as a standalone application, or as a backend for other applications,
and it was built to be easily extended to handle new processing workflows.

The core modules of `paws` 
are pure Python and depend only on PyYAML.
`paws` exposes a simple API
that interacts with these core modules,
for users to write scripts or applications based on `paws`.

The gui modules of `paws`
are built on the `PySide` `Qt` bindings,
and generally aim to provide 
functionality equivalent to the pure Python API,
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


GUI Examples
------------

Instructions and examples for using `paws` through its `Qt`-based GUI
can be found in the documentation. 
NOTE: this is currently false. 
TODO: add this to the docs. 

To keep the package dependencies low,
the PAWS GUI modules are not supported 
by the PyPI package requirements.
Installing PySide (`pip install PySide`)
should provide support for the PAWS GUI.
In future releases, a GUI-enabled version 
may be distributed as a separate package.


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
Citations for your specific operations can be found
by looking those operations up in the `paws` documentation.
NOTE: this is currently false. 
TODO: add this to the docs. 

If the documentation is unclear for the operations you need to cite,
please contact us at `paws-developers@slac.stanford.edu`,
and we will return the correct citation
and fix the missing documentation.

A proper citation for `paws` itself can be found 
in the `paws` documentation.
NOTE: this is currently false. 
TODO: add this to the docs. 


Contribution
------------

Contribution to `paws` is encouraged and appreciated.
Whether you are a researcher looking to contribute Operations to the `paws` library
or a software developer looking to contribute to the platform itself,
the `paws` development team would love to hear from you.
Get in touch with the `paws` development team
at `paws-developers@slac.stanford.edu`.

Full details about contributing to `paws`
can be found in our online documentation.
NOTE: this is currently false. 
TODO: add this to the docs. 


License
-------

The 3-clause BSD-like license attached to this software 
can be found in the LICENSE file in the source code root directory.

