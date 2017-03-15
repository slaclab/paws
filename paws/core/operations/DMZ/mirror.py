import numpy as np

from ...operation import Operation
from ... import optools

class MirrorVertically(Operation):
    """Mirror an image, exchanging top and bottom.

    I.e., mirror an ndarray along axis = 1."""

    def __init__(self):
        input_names = ['image_in', 'channel_2_in', 'channel_3_in']
        output_names = ['image_out', 'channel_2_out', 'channel_3_out']
        super(MirrorVertically, self).__init__(input_names, output_names)
        self.input_doc['image_in'] = '2d ndarray to be mirrored'
        self.input_doc['channel_2_in'] = 'optional second channel/image to be reversed (e.g., noise map)'
        self.input_doc['channel_3_in'] = 'optional third channel/image to be reversed (e.g., mask)'
        self.output_doc['image_out'] = '2d ndarray'
        # source & type
        self.input_src['image_in'] = optools.wf_input
        self.input_src['channel_2_in'] = optools.text_input
        self.input_src['channel_3_in'] = optools.text_input
        # defaults
        self.inputs['channel_2_in'] = None
        self.inputs['channel_3_in'] = None
        self.categories = ['2D DATA PROCESSING','MISC.NDARRAY MANIPULATION']

    def run(self):
        self.outputs['image_out'] = self.inputs['image_in'][:,::-1]
        if self.inputs['channel_2_in'] is not None:
            self.outputs['channel_2_out'] = self.inputs['channel_2_in'][:,::-1]
        else:
            self.outputs['channel_2_out'] = None
        if self.inputs['channel_3_in'] is not None:
            self.outputs['channel_3_out'] = self.inputs['channel_3_in'][:,::-1]
        else:
            self.outputs['channel_3_out'] = None

class MirrorHorizontally(Operation):
    """Mirror an image, exchanging left and right.

    I.e., mirror an ndarray along axis = 0.
    """

    def __init__(self):
        input_names = ['image_in', 'channel_2_in', 'channel_3_in']
        output_names = ['image_out', 'channel_2_out', 'channel_3_out']
        super(MirrorHorizontally, self).__init__(input_names, output_names)
        self.input_doc['image_in'] = '2d ndarray'
        self.input_doc['channel_2_in'] = 'optional second channel/image to be reversed (e.g., noise map)'
        self.input_doc['channel_3_in'] = 'optional third channel/image to be reversed (e.g., mask)'
        self.output_doc['image_out'] = '2d ndarray'
        # source & type
        self.input_src['image_in'] = optools.wf_input

