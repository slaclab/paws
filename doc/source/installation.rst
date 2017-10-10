.. _sec-installation:

Installation
------------

The full PAWS package is available on PyPI.
To install it in an existing Python environment, invoke pip:
``pip install pypaws``

The only dependency of PAWS core packages is pyyaml,
used for serializing and de-serializing workflow data.
pip will automatically install this along with PAWS.

The dependencies of the PAWS Operations 
are not declared as dependencies of PAWS.
This keeps the Python environment relatively lean
and avoids installation overhead,
but it means that users will have to prepare their own environments
for the Operations they want to use.

The PAWS GUI modules are not explicitly supported by the package dependencies.
To use PAWS GUI modules, install PySide into your Python environment:
``pip install PySide``

