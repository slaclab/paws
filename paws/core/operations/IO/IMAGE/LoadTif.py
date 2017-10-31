from collections import OrderedDict
import os.path

import tifffile
import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(image_data=None,dir_path=None,filename=None)

class LoadTif(Operation):
    """
    Takes a filesystem path that points to a .tif,
    outputs image data from the file. 
    """

    def __init__(self):
        super(LoadTif,self).__init__(inputs,outputs)
        self.input_doc['file_path'] = 'path to a .tif image'
        self.output_doc['image_data'] = '2D array representing pixel values'
        self.output_doc['filename'] = 'Filename for image, path and extension stripped'
        
    def run(self):
        p = self.inputs['file_path']
        dir_path = os.path.split(p)[0]
        file_nopath = os.path.split(p)[1]
        file_noext = os.path.splitext(file_nopath)[0]
        self.outputs['dir_path'] = dir_path 
        self.outputs['filename'] = file_noext 
        self.outputs['image_data'] = tifffile.imread(p)

