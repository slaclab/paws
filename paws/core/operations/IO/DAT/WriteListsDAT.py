import os
from collections import OrderedDict

import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(
    col_headers=None,
    format_string=None,
    data_lists=None,
    dir_path=None,
    filename=None,
    filetag='')
outputs=OrderedDict(file_path=None,filename=None)

class WriteListsDAT(Operation):
    """Write a 2d array to a .dat file"""

    def __init__(self):
        super(WriteListsDAT, self).__init__(inputs, outputs)
        self.input_doc['col_headers'] = 'list of column headers (optional)'
        self.input_doc['format_string'] = 'list numpy format strings'
        self.input_doc['data_lists'] = 'list of lists of data- '\
            'there should be as many lists as there are `col_headers`'
        self.input_doc['dir_path'] = 'the path to the destination directory'
        self.input_doc['filename'] = 'the name of the file to be saved- no extension is expected'
        self.input_doc['filetag'] = 'tag appended to filename- no extension is expected'
        self.output_doc['file_path'] = 'the path to the finished dat file: dir_path+filename+filetag+.dat'
        self.output_doc['file_path'] = 'the name of the output file: filename+filetag'

    def run(self):
        col_hdrs = self.inputs['col_headers']
        p = self.inputs['dir_path']
        fnm = self.inputs['filename']
        tag = self.inputs['filetag']
        dat_path = os.path.join(p,self.inputs['filename']+tag+'.dat')
        self.outputs['file_path'] = dat_path
        self.outputs['filename'] = fnm+tag 
        dl = self.inputs['data_lists']

        ncols = len(dl)
        fmt = self.inputs['format_string']
        if fmt is None:
            fmt = ''
            for i in range(ncols):
                fmt += '{!s} \t'
            #if ncols > 0:
            #    fmt = fmt[:-2]

        outfile = open(dat_path,'w')

        n_data = len(dl[0])
        rows = [[col[ri] for col in dl] for ri in range(n_data)]
        #a = np.stack(dl).T

        #if fmt is None:
        #    fmt = '%.18e'
        if col_hdrs is not None:
            h_str = ''
            for hdr in col_hdrs:
                h_str += hdr+' \t'
            outfile.write(h_str + os.linesep)
        for r in rows:
            r_str = fmt.format(*r) + os.linesep
            outfile.write(r_str)
        outfile.close()
        #import pdb; pdb.set_trace()
        #np.savetxt(csv_path, a, fmt=fmt, delimiter=',', newline=os.linesep, header=h_str)

