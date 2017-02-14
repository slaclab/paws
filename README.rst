paws: the Platform for Automated Workflows by SSRL 
==================================================


Description
-----------
`paws` is the Platform for Automated Workflows by SSRL.
It was conceived to serve as a fast, lean, and modular 
workflow manager for image-like data.

At the most basic level, `paws` provides an interface to scripting and executing workflows in Python,
including an ever-growing library of pre-loaded operations and an interface for developing new ones.
Where a researcher might normally build their data processing workflow as a set of scripts, 
the goal of `paws` is to provide intuitive i/o and data management 
to make the scripts run faster, consume less resources, require less human intervention,
and ultimately port into other workflows that use a similar processing step.
Additionally, `paws` provides a GUI for building and configuring workflows, 
networking plugins for data management and control of experimental equipment, 
threaded execution for fast batch processing, 
and a Python api for employing `paws` with minimal overhead (not yet implemented).

`paws` provides a plugin for the `xi-cam` software package,
where the `paws` development team aims to provide a flexible backend
to be called upon by `xi-cam` application plugins.

`paws` is written on the `Qt` platform via the `PySide` bindings.

For complete documentation, please see the `doc` directory of this repository.


Example
-------
An API example will be posted here when the API is released.

Complete instructions for using `paws` through the GUI and through the API (not yet implemented) 
are included in the user manual. 
See the `doc` directory of this repository.


Installation
------------
TODO: put instructions here on how to install paws from PyPI.

The installation instructions from source, for a variety of platforms, 
will be continually added to the main documentation.
Willing users are encouraged to contribute platform-specific documentation at will.


Contribution
------------
Contribution to `paws` is encouraged and appreciated.
Whether you are a researcher looking to contribute a processing routine to the `paws` library,
or a software developer looking to contribute to the platform itself,
the `paws` development team would love to hear from you.

See the manual in the `doc` directory for basic instructions on contributing,
and/or get in touch with the `paws` development team
at `paws-developers@slac.stanford.edu`.

License
-------
The BSD-like license attached to this software 
can be found in the LICENSE file in the source code root directory.

