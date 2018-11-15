import os
from collections import OrderedDict

from ..Workflow import Workflow 
from ...operations.IO.IMAGE.FabIOOpen import FabIOOpen
from ...operations.PROCESSING.INTEGRATION.Integrate1d import Integrate1d
from ...operations.PROCESSING.ZINGERS.EasyZingers1d import EasyZingers1d
from ...operations.IO.NumpySave import NumpySave

inputs = OrderedDict(
    image_file = None,
    image_data = None,
    calib_file = None,
    integrator = None,
    q_min = 0.,
    q_max = float('inf'),
    n_points = 1000.,
    polz_factor = 0.,
    output_dir = None,
    output_filename = None
    )

outputs = OrderedDict(
    q_I = None,
    q_I_dz = None,
    q_I_file = None,
    q_I_dz_file = None
    )

class Integrate(Workflow):

    def __init__(self):
        super(Integrate,self).__init__(inputs,outputs)
        self.add_operations(
            read_image=FabIOOpen(),
            integrate=Integrate1d(),
            dezinger=EasyZingers1d(),
            write_q_I=NumpySave(),
            write_q_I_dz=NumpySave()
            )

    def run(self):
        img_data = self.inputs['image_data'] 
        fn = self.inputs['output_filename'] 
        if self.inputs['image_file']:
            self.operations['read_image'].run_with(file_path=self.inputs['image_file'])
            img_data = self.operations['read_image'].outputs['image_data']
            if not fn: 
                fn = os.path.splitext(os.path.split(self.inputs['image_file'])[1])[0]
        intgtr = self.inputs['integrator']
        if self.inputs['calib_file'] is not None:
            intgtr.set_calib_file(self.inputs['calib_file'])
        if not intgtr.running:
            intgtr.start()
        self.operations['integrate'].run_with(
            integrator = intgtr,
            image_data = img_data,
            npt = self.inputs['n_points'],
            polz_factor = self.inputs['polz_factor']
            )
        all_q_I = self.operations['integrate'].outputs['q_I']
        q_min = self.inputs['q_min']
        q_max = self.inputs['q_max']
        idx_keep = ((all_q_I[:,0] >= q_min) & (all_q_I[:,0] <= q_max))
        q_I = all_q_I[idx_keep,:] 
        self.outputs['q_I'] = q_I 
        q_I_file = os.path.join(self.inputs['output_dir'],fn+'.dat')
        self.outputs['q_I_file'] = q_I_file
        if self.ops_enabled['write_q_I']:
            self.operations['write_q_I'].run_with(
                data = q_I,
                file_path = q_I_file,
                header = 'q (1/Angstrom), Intensity (arb)'
                )

        if self.ops_enabled['dezinger']:
            self.operations['dezinger'].run_with(q_I = q_I)
            q_I_dz = self.operations['dezinger'].outputs['q_I_dz']
            self.outputs['q_I_dz'] = q_I_dz
            q_I_dz_file = os.path.join(self.inputs['output_dir'],fn+'_dz.dat')
            self.outputs['q_I_dz_file'] = q_I_dz_file
            if self.ops_enabled['write_q_I_dz']:
                self.operations['write_q_I_dz'].run_with(
                    data = q_I_dz,
                    file_path = q_I_dz_file,
                    header = 'q (1/Angstrom), Intensity (arb)'
                    )

        return self.outputs

