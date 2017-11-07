"""
The INPUT.CALIBRATION category has operations
for reading in calibration parameters
and converting them between different formats.
Some of the common formats are described here.
Over time, these descriptions should improve.
Contact the paws developers to contribute information 
or report inconsistencies. 


PONI (PyFAI) FORMAT
-------------------

PONI: point of normal incidence.
This is the format used internally by the PyFAI 
(Python Fast Azimuthal Integration) package.
PONI format projects the point-shaped sample orthogonally onto projector plane,
and gives the coordinates of that projection as the PONI,
such that the sample to PONI distance is the shortest distance from sample to detector plane.
coordinate axes: x1 vertical, x2 and x3 horizontal, x3 along beam.
detector axes: with zero rotations, d1 vertical, d2 horizontal, d3 along beam.
axes defined on C format, first dimension is vertical, second dimension is horizontal.
the first dimension (vertical) is fast, the second dimension (horizontal) is slow. 

PONI dict keys and definitions:
- 'dist': distance in meters from sample to PONI on detector plane
- 'poni1': vertical coordinate of PONI on detector axes, in meters
- 'poni2': horizontal coordinate of PONI on detector axes, in meters
- 'rot1': rotation of detector body about x1, applied first, radians
- 'rot2': rotation of detector body about x2, applied second, radians
- 'rot3': rotation of detector body about beam axis x3, applied third, radians
- 'pixel1': pixel dimension along d1 (vertical), meters
- 'pixel2': pixel dimension along d2 (horizontal), meters
- 'wavelength': wavelength in meters
- 'fpolz': polarization factor- not actually a PONI parameter, but it's ok to put it here 
- 'detector': optional pyFAI detector object
- 'splineFile' optional spline file describing detector distortion


NIKA FORMAT
-----------

The calibration performed by the Nika software package
uses a calibrant image, the rectangular pixel dimensions (in mm), 
and the wavelength (in Angstrom), 
to solve the sample to CCD distance in mm,
the position at which the beam axis intersects the detector plane in pixels,
and the horizontal and vertical tilts of the detector in degrees.

Nika does not generate a file to save calibration parameters,
so they have to be recorded by hand in a file.
Paws Operations should be written to read them from a file 
in the following format (one parameter=value per line, no spaces):
- sample_to_CCD_mm=____
- pixel_size_x_mm=____
- pixel_size_y_mm=____
- beam_center_x_pix=____
- beam_center_y_pix=____
- horizontal_tilt_deg=____
- vertical_tilt_deg=____ 
- wavelength_A=____ 


FIT2D FORMAT
------------

Detector plane origin is the bottom left corner of the detector.

Fit2D dict keys and definitions:
- 'directDist': direct distance to detector plane along beam axis, in mm
- 'centerX': horizontal position on the detector plane where the beam intersects, in px
- 'centerY': vertical position on the detector plan where the beam intersects, in px
- 'pixelX': horizontal size of pixel, in um 
- 'pixelY': vertical size of pixel, in um 
- 'tilt': detector tilt in degrees (TODO:clarify)
- 'tiltPlanRotation': detector rotation in degrees = 360 minus WXDIFF alpha (TODO:clarify)
- 'splineFile' optional spline file describing detector distortion

WXDIFF FORMAT
-------------

Similar to Fit2D format,
but knowledge about WXDIFF is hard to come by. 
I hope it can be cleanly documented here over time.
Detector plane origin is the bottom left corner of the detector. 

.calib file lines (and notes): 
- imagetype=uncorrected-q           TODO: describe 
- dtype=uint16                      img data type = unsigned 16-bit integers
- horsize=___                       horizontal extent of image, in pixels
- versize=___                       vertical extent of image, in pixels
- region_ulc_x=___                  TODO: describe  
- region_ulc_y=___                  TODO: describe  
- bcenter_x=___                     horizontal coordinate where the beam axis intersects the detector plane 
- bcenter_y=___                     vertical coordinate where the beam axis intersects the detector plane 
- detect_dist=___                   direct distance from the sample to the detector plane intersection, along the beam axis, in pixels
- detect_tilt_alpha=___             rotation of detector tilt axis plane in radians = 360 minus Fit2D tiltPlanRotation
- detect_tilt_delta=___             detector tilt in radians (TODO:clarify)
- wavelenght=___                    the typo 'wavelenght' is built into wxdiff, and it is reported in angstroms
- Qconv_const=___                   TODO: describe 
"""


