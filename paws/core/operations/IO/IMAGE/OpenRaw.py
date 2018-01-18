from collections import OrderedDict
import os

import PIL 
import numpy as np

from ...Operation import Operation

inputs=OrderedDict(
    file_path=None,
    image_mode=None,
    image_size=None)
outputs=OrderedDict(
    image_data=None,
    PIL_Image=None,
    dir_path=None,
    filename=None)

class OpenRaw(Operation):
    """Get the data out of a .raw image"""

    def __init__(self):
        super(OpenRaw,self).__init__(inputs,outputs) 
        self.input_doc['file_path'] = 'path to a .raw image'
        self.input_doc['image_mode'] = 'PIL.Image mode- '\
            'see http://pillow.readthedocs.io'
        self.input_doc['image_size'] = 'two-element iterable indicating '\
            'the width and height (respectively) of the image'
        self.output_doc['image_data'] = '2D array representing pixel values '\
            'taken from the input file'
        self.output_doc['PIL_Image'] = 'The result of PIL.Image.frombytes()'
        self.output_doc['dir_path'] = 'Path to the directory the image came from'
        self.output_doc['filename'] = 'The image filename, no path, no extension'
        self.input_datatype['file_path'] = 'str'
        self.input_datatype['image_mode'] = 'str'
        self.input_datatype['image_size'] = 'list'
        
    def run(self):
        p = self.inputs['file_path']
        dir_path = os.path.split(p)[0]
        file_nopath = os.path.split(p)[1]
        file_noext = os.path.splitext(file_nopath)[0]
        self.outputs['dir_path'] = dir_path 
        self.outputs['filename'] = file_noext 
        md = self.inputs['image_mode']
        sz = self.inputs['image_size']
        pil_img = PIL.Image.frombytes(md,sz,open(p).read())
        self.outputs['PIL_Image'] = pil_img 
        self.outputs['image_data'] = np.array(pil_img)

