paws: the Platform for Automated Workflows by SSRL 
==================================================


Description
-----------

`paws` stands for the Platform for Automated Workflows by SSRL.
It was conceived to serve as a fast, lean, and modular 
workflow manager for image-like data.

`paws` provides machinery 
to build and execute data processing workflows,
including an ever-growing library of Operations 
that connect together to form a workflow 
with somewhat of a directed graph structure.

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


Installation
------------

TODO: put instructions here on how to install paws from PyPI.
The core modules, being pure Python, 
will be very easy to install from PyPI (not yet implemented).
Because they depend on PySide,
installing the gui modules will be somewhat more complex, 
for those who wish to use the gui.

Contribution
------------

Contribution to `paws` is encouraged and appreciated.
Whether you are a researcher looking to contribute operations to the `paws` library,
or a software developer looking to contribute to the platform itself,
the `paws` development team would love to hear from you.

See the manual in the `doc` directory for basic instructions on contributing,
and/or get in touch with the `paws` development team
at `paws-developers@slac.stanford.edu`.


License
-------

The BSD-like license attached to this software 
can be found in the LICENSE file in the source code root directory.

