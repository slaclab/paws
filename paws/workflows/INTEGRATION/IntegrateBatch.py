import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 
from paws.workflows.INTEGRATION import Integrate 
from paws.operations.IO.FILESYSTEM.BuildFileList import BuildFileList

inputs = OrderedDict(
    image_data = [],
    image_files = [],
    image_dir = None,
    image_regex = None,
    integrator = None,
    q_min = 0.,
    q_max = float('inf'),
    output_dir = None,
    output_filenames = []
    )

outputs = copy.deepcopy(Integrate.outputs)
for k in Integrate.outputs.keys(): outputs[k] = []

class IntegrateBatch(Workflow):

    def __init__(self):
        super(IntegrateBatch,self).__init__(inputs,outputs)
        self.add_operations(
            image_files=BuildFileList(),
            integrate=Integrate.Integrate()
            )

    def run(self):
        self.outputs = copy.deepcopy(outputs)
        img_files = self.inputs['image_files']
        img_data = self.inputs['image_data']
        out_fns = self.inputs['output_filenames']
        if self.inputs['image_dir'] and self.inputs['image_regex']:
            file_outputs = self.operations['image_files'].run_with(
                dir_path = self.inputs['image_dir'],
                regex = self.inputs['image_regex']
                )
            img_files = file_outputs['file_list']
        self.operations['integrate'].set_inputs(
            integrator = self.inputs['integrator'],
            q_min = self.inputs['q_min'],
            q_max = self.inputs['q_max'],
            output_dir = self.inputs['output_dir']
            )
        if not img_data:
            # assume img_files were provided
            img_data = [None for fn in img_files]
        elif not img_files:
            # assume img_data were provided
            img_files = [None for dd in img_data]
        if not out_fns:
            out_fns = [None for fn in img_files]  
        for fn,fd,outfn in zip(img_files,img_data,out_fns):
            if not outfn:
                outfn = os.path.splitext(os.path.split(fn)[1])[0]
            integ_outputs = self.operations['integrate'].run_with(
                image_file = fn,
                image_data = fd,
                output_filename = outfn 
                )
            for out_key, out_data in integ_outputs.items():
                self.outputs[out_key].append(out_data)
        return self.outputs

