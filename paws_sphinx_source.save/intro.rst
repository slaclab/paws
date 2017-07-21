.. _ch-introduction:

Introduction
============

The PAWS package aims to provide 
a fast and lean platform for building and executing workflows for data processing.
It was originally developed to perform analysis of diffraction images 
for research purposes at SLAC/SSRL.
At the core of PAWS is a library of operations,
which are essentially wrappers around useful pieces of Python code.

PAWS itself is a pure Python package.
The PAWS API is meant to provide the functionality of PAWS
such that it can be used in data processing scripts
or employed in the back end of applications.
Limited graphical interfaces are under development
to support specific processing workflows.
Some of these interfaces are included in the PAWS package,
but are not used unless explicitly called upon.
To keep the package dependencies low,
the PAWS GUI modules are not supported by the package dependencies.
The PAWS GUI modules are based on Qt, written by way of the PySide bindings.
Installing PySide (by ``pip install PySide``, for example)
should provide support for the PAWS GUI.
In future releases, the GUI modules may be distributed in a separate package.

Some of the core goals of PAWS:

* Providing turnkey workflows for routine data analysis
* Scaling up of workflows to analyze batches of data
* Portable infrastructure for moving workflows from machine to machine 
* Coupling data analysis to instrumentation for real-time results-driven feedback

The PAWS developers would love to hear from you
if you have wisdom, thoughts, haikus, bugs, artwork, or suggestions.
Get in touch with us at *paws-developers@slac.stanford.edu*.


