from __future__ import print_function
from collections import OrderedDict
import os

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(
    header_dict=None,
    dir_path=None,
    filename=None)

class ReadHeader_SSRL15(Operation):
    """
    Read a .txt header from beamline 1-5 at SSRL into a dict.
    """

    def __init__(self):
        super(ReadHeader_SSRL15, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to a .txt header file produced by beamline 1-5 at SSRL.'
        self.output_doc['header_dict'] = 'the header file as a python dictionary'
        self.output_doc['filename'] = 'filename with path and extension stripped'

    def run(self):
        p = self.inputs['file_path']
        dir_path = os.path.split(p)[0]
        file_nopath = os.path.split(p)[1]
        file_noext = os.path.splitext(file_nopath)[0]
        self.outputs['filename'] = file_noext 
        self.outputs['dir_path'] = dir_path 
        d = OrderedDict()
        for l in open(p,'r').readlines():
           if not l.strip() == '' and not l.strip()[0] == '#':
                kvs = l.split(',')
                # special case for the string headers on line 1
                if not kvs[0].find('User') == -1:
                    u_str = kvs[0].split('User:')[1].strip()
                    t_str = kvs[1].split('time:')[1].strip()
                    d['User'] = u_str
                    d['time'] = t_str
                # and filter out the redundant temperature line
                elif not (len(kvs)==1 and kvs[0].strip()[-1]=='C'):
                    for kv in kvs:
                        kv_arr = kv.split('=')
                        d[kv_arr[0].strip()] = float(kv_arr[1].strip())
        self.outputs['header_dict'] = d

