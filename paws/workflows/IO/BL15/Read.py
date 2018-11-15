from collections import OrderedDict
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

        if self.ops_enabled['read_header']:
            if (self.inputs['header_file']) and (os.path.exists(self.inputs['header_file'])):
                self.operations['read_header'].run_with(
                file_path=self.inputs['header_file'])
            else:
                self.message_callback('header file not found: {}'.format(self.inputs['header_file']))

        if self.ops_enabled['read_image']:
            if (self.inputs['image_file']) and (os.path.exists(self.inputs['image_file'])):
                self.operations['read_image'].run_with(
                file_path=self.inputs['image_file'])
            else:
                self.message_callback('image file not found: {}'.format(self.inputs['image_file']))

        if self.ops_enabled['read_q_I']:
            if (self.inputs['q_I_file']) and (os.path.exists(self.inputs['q_I_file'])):
                self.operations['read_q_I'].run_with(
                file_path=self.inputs['q_I_file'])
            else:
                self.message_callback('q_I file not found: {}'.format(self.inputs['q_I_file']))

        if self.ops_enabled['read_system']:
            if (self.inputs['system_file']) and (os.path.exists(self.inputs['system_file'])):
                self.operations['read_system'].run_with(
                file_path=self.inputs['system_file'])
            else:
                self.message_callback('xrsd system file not found: {}'.format(self.inputs['system_file']))

        hdata = self.operations['read_header'].outputs['data']
        if hdata and self.inputs['time_key']:
           self.outputs['time'] = hdata[self.inputs['time_key']] 

        q_I = None
        dI = None
        if self.ops_enabled['read_q_I']:
            q_I = self.operations['read_q_I'].outputs['data']
            if (q_I is not None) and (q_I.shape[1] > 2):
                q_I = q_I[:,:2]
                dI = q_I[:,2]

        self.outputs.update(
            header_data = hdata, 
            image_data = self.operations['read_image'].outputs['image_data'],
            q_I = q_I,
            dI = dI,
            system = self.operations['read_system'].outputs['system']
            )
        return self.outputs

