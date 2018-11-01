import os
import copy
from collections import OrderedDict

from paws.workflows.Workflow import Workflow 
from paws.workflows.IO.BL15 import Read
from paws.operations.IO.FILESYSTEM.BuildFileList import BuildFileList

inputs = OrderedDict(
    header_dir = None,
    header_regex = '*.yml',
    time_key = None,
    image_dir = None,
    image_ext = '.tif',
    q_I_dir = None,
    q_I_suffix = '',
    q_I_ext = '.dat',
    system_dir = None,
    system_suffix = '',
    system_ext = '.yml'
    )

outputs = copy.deepcopy(Read.outputs)
outputs.update(
    header_files = [],
    image_files = [],
    q_I_files = [],
    system_files = []
    )
for k in Read.outputs.keys(): outputs[k] = []
    

class ReadBatch(Workflow):

    def __init__(self):
        super(ReadBatch,self).__init__(inputs,outputs)
        self.add_operation('header_files',BuildFileList())
        self.add_operation('read',Read.Read())

    def run(self):
        self.operations['header_files'].run_with(
            dir_path = self.inputs['header_dir'],
            regex = self.inputs['header_regex']
            )
        header_file_list = self.operations['header_files'].outputs['file_list']
        self.outputs['header_files'] = header_file_list
        filename_list = [os.path.splitext(os.path.split(hf)[1])[0] for hf in header_file_list]
        q_I_suffix = self.inputs['q_I_suffix']
        sys_suffix = self.inputs['system_suffix']
        img_ext = self.inputs['image_ext']
        q_I_ext = self.inputs['q_I_ext']
        sys_ext = self.inputs['system_ext']
        if not img_ext[0] == '.': img_ext='.'+img_ext
        if not q_I_ext[0] == '.': q_I_ext='.'+q_I_ext
        if not sys_ext[0] == '.': sys_ext='.'+sys_ext
        img_dir = self.inputs['image_dir']
        image_file_list = [os.path.join(img_dir,fn+img_ext) for fn in filename_list]
        self.outputs['image_files'] = image_file_list
        q_I_dir = self.inputs['q_I_dir']
        q_I_file_list = [os.path.join(q_I_dir,fn+q_I_suffix+q_I_ext) for fn in filename_list]
        self.outputs['q_I_files'] = q_I_file_list
        sys_dir = self.inputs['system_dir']
        system_file_list = [os.path.join(sys_dir,fn+sys_suffix+sys_ext) for fn in filename_list]
        self.outputs['system_files'] = system_file_list

        n_hdrs = len(filename_list)
        self.message_callback('STARTING BATCH ({})'.format(n_hdrs))
        for ihdr, hdr_fn, img_fn, q_I_fn, sys_fn in zip(range(n_hdrs),
        header_file_list,image_file_list,q_I_file_list,system_file_list):
            self.message_callback('RUNNING {} / {}'.format(ihdr,n_hdrs))
            outs = self.operations['read'].run_with(
                header_file = hdr_fn,
                time_key = self.inputs['time_key'],
                image_file = img_fn,
                q_I_file = q_I_fn,
                system_file = sys_fn
                )        
            for out_key, out_data in outs.items():
                self.outputs[out_key].append(out_data)
        return self.outputs

