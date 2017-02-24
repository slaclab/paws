import os.path

import tifffile
import numpy as np

from ...operation import Operation
from ... import optools

class LoadTif(Operation):
    """
    Takes a filesystem path that points to a .tif,
    outputs image data and metadata from the file. 
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['image_data','filename']
        super(LoadTif,self).__init__(input_names,output_names)
        self.input_doc['path'] = 'path to a .tif image'
        self.input_src['path'] = optools.fs_input
        self.input_type['path'] = optools.path_type
        self.output_doc['image_data'] = '2D array representing pixel values'
        self.output_doc['filename'] = 'Filename for image, directories excluded'
        
    def run(self):
        img_url = self.inputs['path']
        self.outputs['filename'] = os.path.split(self.inputs['path'])[1]
        try:
            self.outputs['image_data'] = tifffile.imread(self.inputs['path'])
        except IOError as ex:
            ex.message = "[{}] IOError for file {}. \nError message:".format(__name__,img_url,ex.message)
            raise ex
        except ValueError as ex:
            ex.message = "[{}] ValueError for file {}. \nError message:".format(__name__,img_url,ex.message)
            raise ex
