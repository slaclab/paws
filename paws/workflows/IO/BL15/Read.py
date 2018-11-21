from collections import OrderedDict
import copy
import os

from ...Workflow import Workflow 
from ....operations.IO.YAML.LoadYAML import LoadYAML
from ....operations.IO.YAML.LoadXRSDSystem import LoadXRSDSystem
from ....operations.IO.IMAGE.FabIOOpen import FabIOOpen
from ....operations.IO.NumpyLoad import NumpyLoad

# NOTE: this workflow is for reading samples
# that were saved with YAML headers

inputs = OrderedDict(
    header_file = None,
    time_key = 't_utc',
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
        self.add_operations(
            read_header=LoadYAML(),
            read_image=FabIOOpen(),
            read_q_I=NumpyLoad(),
            read_system=LoadXRSDSystem()
            )

    def run(self):
        self.outputs = copy.deepcopy(outputs)

        if self.ops_enabled['read_header']:
            if (self.inputs['header_file']) and (os.path.exists(self.inputs['header_file'])):
                hdr_outs = self.operations['read_header'].run_with(
                file_path=self.inputs['header_file'])
                hdata = hdr_outs['data']
                self.outputs['header_data'] = hdata
                if hdata and self.inputs['time_key']:
                    self.outputs['time'] = hdata[self.inputs['time_key']] 
            else:
                self.message_callback('header file not found: {}'.format(self.inputs['header_file']))

        if self.ops_enabled['read_image']:
            if (self.inputs['image_file']) and (os.path.exists(self.inputs['image_file'])):
                img_outs = self.operations['read_image'].run_with(
                file_path=self.inputs['image_file'])
                self.outputs['image_data'] = img_outs['image_data']
            else:
                self.message_callback('image file not found: {}'.format(self.inputs['image_file']))

        if self.ops_enabled['read_q_I']:
            if (self.inputs['q_I_file']) and (os.path.exists(self.inputs['q_I_file'])):
                q_I_outs = self.operations['read_q_I'].run_with(
                file_path=self.inputs['q_I_file'])
                q_I = q_I_outs['data']
                dI = None
                if (q_I is not None) and (q_I.shape[1] > 2):
                    q_I = q_I[:,:2]
                    dI = q_I[:,2]
                self.outputs['q_I'] = q_I
                self.outputs['dI'] = dI
            else:
                self.message_callback('q_I file not found: {}'.format(self.inputs['q_I_file']))

        if self.ops_enabled['read_system']:
            if (self.inputs['system_file']) and (os.path.exists(self.inputs['system_file'])):
                sys_outs = self.operations['read_system'].run_with(
                file_path=self.inputs['system_file'])
                self.outputs['system'] = sys_outs['system']
            else:
                self.message_callback('xrsd system file not found: {}'.format(self.inputs['system_file']))

        return self.outputs

