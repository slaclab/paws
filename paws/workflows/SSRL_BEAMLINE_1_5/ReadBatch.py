from collections import OrderedDict
import os
import copy

from ..Workflow import Workflow 
from . import Read
from ...operations.FILESYSTEM.BuildFileList import BuildFileList

inputs = OrderedDict(
    header_dir = '',
    header_regex = '*.yml',
    header_suffix = '',
    #header_filter_regex = '.*',
    image_dir = '',
    image_suffix = '',
    image_ext = '.tif',
    q_I_dir = '',
    q_I_suffix = '',
    q_I_ext = '.dat',
    system_dir = '',
    system_suffix = '',
    system_ext = '.yml'
    )

outputs = copy.deepcopy(Read.outputs)
for k in Read.outputs.keys(): outputs[k] = []
outputs.update(
    filenames = [],
    header_files = [],
    image_files = [],
    q_I_files = [],
    system_files = []
    )

class ReadBatch(Workflow):

    def __init__(self):
        super(ReadBatch,self).__init__(inputs,outputs)
        self.list_header_files = BuildFileList()
        self.reader = Read.Read()

    def run(self):
        # initialize outputs in case of Workflow re-use!
        self.outputs = copy.deepcopy(outputs)
        self.list_header_files.run_with(
            dir_path = self.inputs['header_dir'],
            regex = self.inputs['header_regex']
            )
        header_file_list = self.list_header_files.outputs['file_list']
        self.outputs['header_files'] = header_file_list
        filename_list = [os.path.splitext(os.path.split(hf)[1])[0] for hf in header_file_list]
        hdr_fn_sfx = self.inputs['header_suffix']
        if hdr_fn_sfx: filename_list = [fn[:fn.rfind(hdr_fn_sfx)] for fn in filename_list]

        self.outputs['filenames'] = filename_list 
        q_I_dir = self.inputs['q_I_dir']
        q_I_suffix = self.inputs['q_I_suffix']
        q_I_ext = self.inputs['q_I_ext']
        img_dir = self.inputs['image_dir']
        img_sfx = self.inputs['image_suffix']
        img_ext = self.inputs['image_ext']
        sys_dir = self.inputs['system_dir']
        sys_suffix = self.inputs['system_suffix']
        sys_ext = self.inputs['system_ext']
        if not img_ext[0] == '.': img_ext='.'+img_ext
        if not q_I_ext[0] == '.': q_I_ext='.'+q_I_ext
        if not sys_ext[0] == '.': sys_ext='.'+sys_ext
        image_file_list = [None for fn in filename_list]
        if img_dir and img_ext:
            image_file_list = [os.path.join(img_dir,fn+img_sfx+img_ext) for fn in filename_list]
        self.outputs['image_files'] = image_file_list
        q_I_file_list = [None for fn in filename_list]
        if q_I_dir and q_I_ext:
            q_I_file_list = [os.path.join(q_I_dir,fn+q_I_suffix+q_I_ext) for fn in filename_list]
        self.outputs['q_I_files'] = q_I_file_list
        system_file_list = [None for fn in filename_list]
        if sys_dir and sys_ext:
            system_file_list = [os.path.join(sys_dir,fn+sys_suffix+sys_ext) for fn in filename_list]
        self.outputs['system_files'] = system_file_list

        n_hdrs = len(filename_list)
        self.message_callback('STARTING BATCH ({})'.format(n_hdrs))
        for ihdr, hdr_fn, img_fn, q_I_fn, sys_fn in zip(range(n_hdrs),
        header_file_list,image_file_list,q_I_file_list,system_file_list):
            self.message_callback('RUNNING {} / {}'.format(ihdr+1,n_hdrs))
            outs = self.reader.run_with(
                header_file = hdr_fn,
                image_file = img_fn,
                q_I_file = q_I_fn,
                system_file = sys_fn
                )        
            for out_key, out_data in outs.items():
                self.outputs[out_key].append(out_data)
        return self.outputs

