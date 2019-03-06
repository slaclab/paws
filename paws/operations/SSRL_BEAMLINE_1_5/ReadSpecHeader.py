from collections import OrderedDict
import os
import datetime
import time

import tzlocal

from ..Operation import Operation

inputs=OrderedDict(
    file_path=None,
    temperature_key='TEMP')

outputs=OrderedDict(
    data=None,
    dir_path=None,
    filename=None)

class ReadSpecHeader(Operation):
    """
    Read a .txt header from beamline 1-5 at SSRL into a dict.
    """

    def __init__(self):
        super(ReadSpecHeader, self).__init__(inputs, outputs)
        self.input_doc['file_path'] = 'path to a .txt header file produced by beamline 1-5 at SSRL.'
        self.output_doc['data'] = 'the header data, packaged as a python dictionary'
        self.output_doc['dir_path'] = 'directory path'
        self.output_doc['filename'] = 'filename with path and extension stripped'

    def run(self):
        p = self.inputs['file_path']
        dir_path,filename = os.path.split(p)
        file_noext = os.path.splitext(filename)[0]
        self.outputs['filename'] = file_noext 
        self.outputs['dir_path'] = dir_path 
        d = OrderedDict()
        self.message_callback('reading {}'.format(p))
        for l in open(p,'r').readlines():
           if not l.strip() == '' and not l.strip()[0] == '#':
                kvs = l.split(',')
                # special case for the string headers on line 1
                if not kvs[0].find('User') == -1:
                    u_str = kvs[0].split('User:')[1].strip()
                    t_str = kvs[1].split('time:')[1].strip()
                    d['User'] = u_str
                    d['date_time'] = t_str
                    tz = tzlocal.get_localzone()
                    # use strptime to create a naive datetime
                    dt = datetime.datetime.strptime(t_str.strip(),"%a %b %d %H:%M:%S %Y")
                    # add timezone information to datetime
                    dt_aware = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,dt.microsecond,tz)
                    # interpret the time in UTC 
                    t = time.mktime(dt_aware.timetuple())
                    d['time'] = float(t)
                # and filter out the redundant temperature line
                elif not (len(kvs)==1 and kvs[0].strip()[-1]=='C'):
                    for kv in kvs:
                        kv_arr = kv.split('=')
                        d[kv_arr[0].strip()] = float(kv_arr[1].strip())
        # add 'temperature' to the output data,
        # to make a consistent interface with the non-legacy header reader
        if self.inputs['temperature_key'] in d:
            d['temperature'] = d[self.inputs['temperature_key']]
        else:
            d['temperature'] = None
        self.outputs['data'] = d
        return self.outputs

