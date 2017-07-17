import os.path

import tifffile
import numpy as np

from ... import Operation as op
from ...Operation import Operation

class LoadTif(Operation):
    """
    Takes a filesystem path that points to a .tif,
    outputs image data from the file. 
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['image_data','filename']
        super(LoadTif,self).__init__(input_names,output_names)
        self.input_doc['path'] = 'path to a .tif image'
        self.input_src['path'] = op.fs_input
        self.input_type['path'] = op.path_type
        self.output_doc['image_data'] = '2D array representing pixel values'
        self.output_doc['filename'] = 'Filename for image, path and extension stripped'
        
    def run(self):
        p = self.inputs['path']
        file_nopath = os.path.split(p)[1]
        file_noext = os.path.splitext(file_nopath)[0]
        self.outputs['filename'] = file_noext 
        try:
            self.outputs['image_data'] = tifffile.imread(p)
        except IOError as ex:
            ex.message = "[{}] IOError for file {}. \nError message:".format(__name__,p,ex.message)
            raise ex
        except ValueError as ex:
            ex.message = "[{}] ValueError for file {}. \nError message:".format(__name__,p,ex.message)
            raise ex

