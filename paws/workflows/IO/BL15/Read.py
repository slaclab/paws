from collections import OrderedDict
import copy
import os

from xrsdkit.tools import ymltools as xrsdyml

from ...Workflow import Workflow 
from ....operations.IO.YAML.LoadYAML import LoadYAML
from ....operations.IO.IMAGE.FabIOOpen import FabIOOpen
from ....operations.IO.NumpyLoad import NumpyLoad

# NOTE: this workflow is for reading samples
# that were saved with YAML headers

inputs = OrderedDict(
    header_file = None,
    image_file = None,
    q_I_file = None,
    system_file = None
    )

outputs = OrderedDict(
    time = None,
    header_data = None,
    image_data = None,
    q_I = None,
    dI = None,
    system = None
    )

class Read(Workflow):

    def __init__(self):
        super(Read,self).__init__(inputs,outputs)
        self.header_reader = LoadYAML()
        self.image_reader = FabIOOpen()
        self.q_I_reader = NumpyLoad()

    def run(self):
        self.outputs = copy.deepcopy(outputs)

        if (self.inputs['header_file']) and (os.path.exists(self.inputs['header_file'])):
            hdr_outs = self.header_reader.run_with(
            file_path = self.inputs['header_file'])
            hdata = hdr_outs['data']
            self.outputs['header_data'] = hdata
            self.outputs['time'] = hdata['time']
        elif self.inputs['header_file']:
            self.message_callback('header file not found: {}'.format(self.inputs['header_file']))

        if (self.inputs['image_file']) and (os.path.exists(self.inputs['image_file'])):
            img_outs = self.image_reader.run_with(
            file_path=self.inputs['image_file'])
            self.outputs['image_data'] = img_outs['image_data']
        elif self.inputs['image_file']:
            self.message_callback('image file not found: {}'.format(self.inputs['image_file']))

        if (self.inputs['q_I_file']) and (os.path.exists(self.inputs['q_I_file'])):
            q_I_outs = self.q_I_reader.run_with(
            file_path=self.inputs['q_I_file'])
            q_I = q_I_outs['data']
            dI = None
            if (q_I is not None) and (q_I.shape[1] > 2):
                q_I = q_I[:,:2]
                dI = q_I[:,2]
            self.outputs['q_I'] = q_I
            self.outputs['dI'] = dI
        elif self.inputs['q_I_file']:
            self.message_callback('q_I file not found: {}'.format(self.inputs['q_I_file']))

        if (self.inputs['system_file']) and (os.path.exists(self.inputs['system_file'])):
            self.message_callback('loading {}'.format(self.inputs['system_file']))
            self.outputs['system'] = xrsdyml.load_sys_from_yaml(self.inputs['system_file'])
        else:
            self.message_callback('xrsd system file not found: {}'.format(self.inputs['system_file']))

        return self.outputs

