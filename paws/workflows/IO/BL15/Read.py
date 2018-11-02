from collections import OrderedDict

from paws.workflows.Workflow import Workflow 
from paws.operations.IO.YAML.LoadYAML import LoadYAML
from paws.operations.IO.YAML.LoadXRSDSystem import LoadXRSDSystem
from paws.operations.IO.IMAGE.FabIOOpen import FabIOOpen
from paws.operations.IO.NumpyLoad import NumpyLoad

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
            self.operations['read_header'].run_with(
            file_path=self.inputs['header_file'])
        if self.ops_enabled['read_image']:
            self.operations['read_image'].run_with(
            file_path=self.inputs['image_file'])
        if self.ops_enabled['read_q_I']:
            self.operations['read_q_I'].run_with(
            file_path=self.inputs['q_I_file'])
        if self.ops_enabled['read_system']:
            self.operations['read_system'].run_with(
            file_path=self.inputs['system_file'])
        hdata = self.operations['read_header'].outputs['data']
        if hdata and self.inputs['time_key']:
           self.outputs['time'] = hdata[self.inputs['time_key']] 
        self.outputs.update(
            header_data = hdata, 
            image_data = self.operations['read_image'].outputs['image_data'],
            q_I = self.operations['read_q_I'].outputs['data'],
            system = self.operations['read_system'].outputs['system']
            )
            #time = self.read_header.outputs['data']['t_utc'],
            #temperature = self.read_header.outputs['data']['temperature'],
        return self.outputs

