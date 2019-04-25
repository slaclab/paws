from collections import OrderedDict
import time
import copy
import os

import yaml
import fabio

from ...Workflow import Workflow
from ....pawstools import primitives

inputs = OrderedDict(
    flow_reactor=None, 
    spec_infoclient=None,
    ssh_client=None,
    ssh_data_dir='/home/data',
    recipe={},
    delay_time=60.,
    n_exposures=1,
    exposure_time=10.,
    header_data={},
    reaction_id='anonymous',
    header_output_dir=None,
    image_output_dir=None
    )

outputs = OrderedDict(
    headers=[],
    images=[],
    header_paths=[],
    image_paths=[]
    )

class RunRecipeTakeImages(Workflow):

    def __init__(self):
        super(RunRecipeTakeImages,self).__init__(inputs,outputs)

    def run(self):

        # set recipe, delay for reactor flush
        self.inputs['flow_reactor'].set_recipe(self.inputs['recipe'])
        self.message_callback('blocking {} seconds to flush reactor'.format(self.inputs['delay_time']))
        time.sleep(self.inputs['delay_time'])

        # copy the input header to build image headers
        rxn_id = self.inputs['reaction_id']
        hdr_data = copy.deepcopy(self.inputs['header_data'])
        hdr_data['reaction_id'] = rxn_id 

        # expose images, augment and save headers
        for iexp in range(self.inputs['n_exposures']):
            hdr = copy.deepcopy(hdr_data)
            hdr.update(self.inputs['flow_reactor'].get_state())
            fn_root = rxn_id+'_exp{}'.format(iexp)
            self.inputs['spec_infoclient'].mar_expose(fn_root,self.inputs['exposure_time'])
            tmstmp = self.inputs['flow_reactor'].timer.get_epoch_time()
            smpl_id = rxn_id+'_{}'.format(int(tmstmp))
            hdr.update(time=tmstmp,
                reaction_id=rxn_id,
                sample_id=smpl_id,
                exposure_time=self.inputs['exposure_time']
                )
            self.outputs['headers'].append(hdr)
            if self.inputs['header_output_dir']:
                hdr_path = os.path.join(self.inputs['header_output_dir'],fn_root+'.yml')
                yaml.dump(primitives(hdr),open(hdr_path,'w'))
                self.outputs['header_paths'].append(hdr_path)

        # fetch images
        if self.inputs['image_output_dir']:
            for iexp in range(self.inputs['n_exposures']):
                fn_root = rxn_id+'_exp{}'.format(iexp)
                img_fn = fn_root+'_0001.tif'
                mar_path = self.inputs['ssh_data_dir']+'/'+img_fn
                local_path = os.path.join(self.inputs['image_output_dir'],img_fn)
                self.inputs['ssh_client'].copy_file(mar_path,local_path)
                img = fabio.open(local_path).data
                self.outputs['images'].append(img)
                self.outputs['image_paths'].append(local_path)

        # pause the reactor, then return
        self.inputs['flow_reactor'].set_temperature(25.)
        self.inputs['flow_reactor'].stop_pumps()
        return self.outputs

