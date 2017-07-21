from os.path import splitext, split
from collections import OrderedDict

from ... import Operation as op
from ...Operation import Operation

class ReadHeader_SSRL15(Operation):
    """
    Read a .txt header from beamline 1-5 at SSRL into a dict.
    """

    def __init__(self):
        input_names = ['txt_path']
        output_names = ['header_dict', 'filename']
        super(ReadHeader_SSRL15, self).__init__(input_names, output_names)
        self.input_src['txt_path'] = op.fs_input
        self.input_type['txt_path'] = op.path_type
        self.input_doc['txt_path'] = str('path to a txt header file produced by beamline 1-5 at SSRL.')
        self.output_doc['header_dict'] = 'the header file as a python dictionary'
        self.output_doc['filename'] = 'filename with path and extension stripped'

    def run(self):
        txt_path = self.inputs['txt_path']
        filename = split(txt_path)[1]
        filename_noext = splitext(filename)[0]
        self.outputs['filename'] = filename_noext 
        d = OrderedDict()
        for l in open(txt_path,'r').readlines():
            try:
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
            except Exception as e:
                d['ERROR'] = e.message
                self.outputs['header_dict'] = d
                raise e

