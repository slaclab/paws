paws: the Platform for Automated Workflows by SSRL 
==================================================


Description
-----------

`paws` stands for the Platform for Automated Workflows by SSRL.
It was conceived to serve as a fast, lean, and modular 
workflow manager for image-like data.

`paws` provides machinery 
to build and execute data processing workflows,
including an ever-growing library of pre-loaded Operations 
and an interface for developing new ones.
The user loads a set of Operations
and connects their inputs and outputs 
to form a workflow that is something like a directed graph
with structured nodes.

The core modules of `paws` 
are pure Python and have very few dependencies.
The package currently exposes a simple API
that interacts with these core modules,
for users to write scripts based on `paws`,
or to import the `paws` API to perform
back-end computations for other applications or widgets.

The `paws` package also includes a graphical application 
built on the `PySide` `Qt` bindings.
Its GUI is similar to the interface for `Xi-cam`.
Through this GUI, users can build and configure workflows, 
examine existing `paws` Operations,
develop new `paws` Operations,
and visualize the outputs of their workflows.
Note that this graphical application
was built to exist "on top" of `paws`,
not as an integral part of the package.
As such, there is plenty of potential to develop
improved or simplified graphical applications or widgets,
with `paws` workflows running in the back end.

Each Operation is a self-contained object,
so that after its inputs are loaded, 
the Operation can be moved to another host and executed remotely, 
as long as the host environment 
fulfills the dependencies of the Operation. 
A `paws` Operation may depend on any number of other packages
(many of them depend on `numpy` or `scipy` for example),
but Operations are not imported until they are enabled,
so the user's platform is only required to fulfill dependencies
for the Operations they actually want to use
(TODO: this import functionality is not yet implemented). 


Example
-------

TODO: Get the docs online, link to them here.
TODO: link to Nika, PyFAI, and matplotlib here.

Here is an example of how to use `paws` 
to write a data processing script.
This script performs a common diffraction data processing workflow:
it reads some calibration parameters (in Nika format),
converts them to PONI (PyFAI) format,
reads an image, uses the calibration parameters 
to calibrate and reduce the image with PyFAI,
and windows the useful part of the data.
After executing, the useful data is extracted
and plotted using matplotlib.

.. code-block:: python
    import paws.api
    from matplotlib import pyplot as plt

    mypaw = paws.api.start()

    # Start a workflow, name it
    mypaw.add_wf('test')

    # Instantiate operations, name them, add them to the workflow
    mypaw.add_op('read_cal','INPUT.CALIBRATION.NikaToPONI')
    mypaw.add_op('read_img','INPUT.TIF.LoadTif')
    mypaw.add_op('cal_reduce','PROCESSING.CALIBRATION.CalReduce')
    mypaw.add_op('window','PACKAGING.WindowZip')

    # Set up the input routing: 
    # WXDToPONI reads a WXDiff calibration result 
    # and translates it to PONI (PyFAI) format
    mypaw.set_input('read_cal', 'wxd_file',
    src='filesystem', tp='path', val='/path/to/file.nika')

    # LoadTif loads a tif image
    mypaw.set_input('read_img', 'path',
    src='filesystem', tp='path', val='/path/to/image.tif')
    
    # CalReduce takes a PONI dict and an image,
    # calibrates and reduces to I(q) vs. q
    mypaw.set_input('cal_reduce', 'poni_dict',
    src='workflow', tp='reference', val='read_cal.outputs.poni_dict')
    mypaw.set_input('cal_reduce', 'image_data',
    src='workflow', tp='reference', val='read_img.outputs.image_data')

    # WindowZip takes x and y data and a window (xmin<x<xmax),
    # outputs the x and y data that live within the window
    mypaw.set_input('window','x',
    src='workflow', tp='reference', val='cal_reduce.outputs.q')
    mypaw.set_input('window','y',
    src='workflow', tp='reference', val='cal_reduce.outputs.I')
    mypaw.set_input('window','x_min', src='text', tp='float', val=0.02)
    mypaw.set_input('window','x_max', src='text', tp='float', val=0.6)

    # Execute the workflow
    mypaw.execute()

    # Grab the reduced data
    q_I_out = mypaw.get_output('window','x_y_window')

    # Plot the reduced data
    plt.semilogy(q_I_out[:,0],q_I_out[:,1])
    plt.show()

Complete instructions are included in the user manual. 
See the `doc` directory of this repository.


Installation
------------

TODO: put instructions here on how to install paws from PyPI.
The core modules, being pure Python, 
will be very easy to install from PyPI (not yet implemented).

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

