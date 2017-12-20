from collections import OrderedDict
import os

from pypif import pif
import pypif.obj as pifobj 

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(pif=None,dir_path=None,filename=None)
outputs=OrderedDict(file_path=None)
        
class SavePIFAsJSON(Operation):

    def __init__(self):
        super(SavePIFAsJSON,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['dir_path'] = 'Path to system directory where .json file will be created' 
        self.input_doc['filename'] = 'Name of the .json file to be created. '\
            'The .json extension is appended automatically if not provided.' 
        self.output_doc['file_path'] = 'Full path to the newly saved .json file'

    def run(self):
        p = self.inputs['pif']        
        dp = self.inputs['dir_path']
        fn = self.inputs['filename']
        if not os.path.splitext(fn)[1] == 'json':
            fn = fn+'.json'
        json_file = os.path.join(dp,fn)
        self.outputs['file_path'] = json_file
        pif.dump(p, open(json_file,'w'))

