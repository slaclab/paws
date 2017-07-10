.. _ch-introduction:

Introduction
============

The ``paws`` package aims to provide 
a fast and lean platform for building and executing workflows for data processing.
It was originally developed to perform analysis of diffraction images 
for research purposes at SLAC/SSRL.
At the core of ``paws`` is a workflow engine
that uses a library of operations
to crunch through data and expose select results 
while attempting to minimize resource consumption.

``paws`` is currently written in Python,
based on Qt via the PySide bindings.
Internally, ``paws`` keeps track of data in Qt-based tree models,
which can be controlled either directly (through the paws api)
or through a gui (employing the Qt model-view framework).

``paws`` also provides an interface to ``xi-cam``,
a synchrotron x-ray diffraction data analysis package
written by the CAMERA Institute and 
Pandolfi, et al at the Lawrence Berkeley National Lab.

Some the core goals of ``paws``:

* Eliminate redundant development efforts 
* Streamline and standardize routine data analysis
* Simplify data storage and provide large-scale analysis 
* Perform data analysis in real time for results-driven feedback

The ``paws`` developers would love to hear from you
if you have wisdom, thoughts, haikus, bugs, artwork, or suggestions.
Limericks are also welcome.
Get in touch with us at ``paws-developers@slac.stanford.edu``.


