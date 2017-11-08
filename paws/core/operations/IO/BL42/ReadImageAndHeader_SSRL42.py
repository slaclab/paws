import os
from collections import OrderedDict
import re

import tifffile
import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(
    image_data=None,
    image_header=None,
    dir_path=None,
    filename=None)

class ReadImageAndHeader_SSRL42(Operation):
    """Read image and header from SSRL beam line 4-2."""

    def __init__(self):
        super(ReadImageAndHeader_SSRL42, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to a tif file '\
            'produced by beamline 4-2 at SSRL. '\
            'A .prp header file is expected '\
            'in the same directory as this .tif file.'
        self.output_doc['image_data'] = 'the image data as an ndarray'
        self.output_doc['image_header'] = 'the header data as a python dictionary'
        self.output_doc['dir_path'] = 'the directory portion of the input file_path'
        self.output_doc['filename'] = 'the filename with path and extension stripped'

    def run(self):
        tif_path = self.inputs['file_path']
        dirpath,filename = os.path.split(tif_path)
        filename_noext = os.path.splitext(filename)[0]
        path_noext = os.path.splitext(tif_path)[0]
        hdr_file_path = path_noext + '.prp'
        self.outputs['dir_path'] = dirpath 
        self.outputs['filename'] = filename_noext 
        img = tifffile.imread(tif_path)
        # flip the image...
        self.outputs['image_data'] = np.array(img[::-1,:])
        d = OrderedDict()
        for l in open(hdr_file_path,'r').readlines():
            if not '=' in l:
                if l[:4] == 'Time':
                    d['time'] = l.split('Time this file was written: ')[1]
            else:
                kv = l.split('=')
                if kv[0] == 'Detector mode':
                    d[kv[0]] = kv[1].split(' ')[0].replace(';','')
                elif kv[0] in ['Beam energy','Pipe length',
                    'Horizontal position','Vertical position',
                    'dispx position','dispy position']:
                    # Split off and throw away the unit specification
                    d[kv[0]] = float(kv[1].split(' ')[0])
                elif kv[0] in ['Exposure time','Counting time','Phi position']:
                    # Units not specified: save float directly.
                    d[kv[0]] = float(kv[1])
                elif kv[0] in ['Scan motor','Scan range']:
                    d[kv[0]] = kv[1]
                else:
                    # Use key and value directly,
                    # use re.sub to filter out parentheticals 
                    d[re.sub('\(.*\)','',kv[0])] = float(re.sub('\(.*\)','',kv[1]))
            self.outputs['image_header'] = d

