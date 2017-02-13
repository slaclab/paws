## Synopsis

`paws` is the Platform for Automated Workflows by SSRL.
It was conceived to serve as a fast, lean, and modular 
workflow manager for image-like data.

At the most basic level, `paws` provides an interface 
to the entirety of the Python programming language,
featuring an ever-growing library of pre-loaded operations
and an interface for developing new operations.
Where a researcher might normally build their data processing workflow as a set of scripts, 
the goal of `paws` is to provide intuitive i/o and data management 
to make the scripts run faster, consume less resources, and require less human intervention.
Additionally, `paws` provides a GUI for building and configuring data processing workflows, 
networking tools for data management and control of experimental equipment, 
threaded execution for fast batch processing, 
and a Python api for employing `paws` with minimal overhead.

`paws` is written in `Qt` via the `PySide` bindings.
This allows the `paws` gui to run within other `Qt` based applications.
In this way, `paws` is provided as a plugin for the `xi-cam` software package.

For complete documentation, please see the `doc` directory of this repository.

## Code Example

Instructions for using `paws` 
through the GUI and through the API (not yet implemented)
are included in the user manual. 
See the `doc` directory of this repository.
A low-overhead usage example will eventually be posted here.

## Motivation

The goal of `paws` is to make processing of image-like data 
fast, intuitive, and customizable, all at the same time.
Processing includes input, basic operations, visualization, 
and storage of raw and processed data.
An eventual goal is to leverage 
processing capabilities and access to data stores
to provide feedback to control parameters of an experiment. 

## Installation

`paws` will soon be packaged as a Python wheel.
TODO: put instructions here on how to install the wheel.

The installation instructions for a variety of platforms from source,
included in the user manual, will be continually updated.

## API Reference

The API is not yet implemented. It will be described here.

## Tests

TODO: Write a test suite for `paws`.
Put instructions here on how to run and interpret the test suite.

## Contributors

Contribution to `paws` is encouraged!
Please fork the repository and submit a pull request.
See the manual in the `doc` directory for detailed instructions. 
Get in touch with the `paws` development team
at `slacx-developers@slac.stanford.edu`.

## License

Currently this code is free and open-source. 
It will be distributed with some kind of license in the near future.

