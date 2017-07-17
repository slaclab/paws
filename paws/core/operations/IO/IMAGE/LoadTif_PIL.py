import numpy as np
from PIL import Image

from ... import Operation as op
from ...Operation import Operation

class LoadTif_PIL(Operation):
    """
    Takes a filesystem path that points to a .tif,
    outputs image data and metadata from the file. 
    """

    def __init__(self):
        input_names = ['path']
        output_names = ['image_data','metadata']
        super(LoadTif_PIL,self).__init__(input_names,output_names)
        self.input_doc['path'] = 'path to a .tif image'
        self.input_src['path'] = op.fs_input
        self.input_type['path'] = op.path_type
        self.output_doc['image_data'] = '2D array representing pixel values'
        self.output_doc['metadata'] = 'Dictionary of image metadata'
        
    def run(self):
        img_url = self.inputs['path']
        try:
            pil_img = Image.open(img_url)
            self.outputs['image_data'] = np.array(pil_img)
            self.outputs['metadata'] = pil_img.info
        except IOError as ex:
            ex.message = "[{}] IOError for file {}. \nError message:".format(__name__,img_url,ex.message)
            raise ex
        except ValueError as ex:
            ex.message = "[{}] ValueError for file {}. \nError message:".format(__name__,img_url,ex.message)
            raise ex

