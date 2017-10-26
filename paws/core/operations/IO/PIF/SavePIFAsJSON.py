import os

from pypif import pif
import pypif.obj as pifobj 

from ... import Operation as opmod 
from ...Operation import Operation
        
class SavePIFAsJSON(Operation):

    def __init__(self):
        input_names = ['pif','dirpath','filename']
        output_names = ['file_path']
        super(SavePIFAsJSON,self).__init__(input_names,output_names)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['dirpath'] = 'Path to system directory where .json file will be created' 
        self.input_doc['filename'] = 'Name of the .json file to be created. '\
            'The .json extension is appended automatically if not provided.' 
        self.output_doc['file_path'] = 'Full path to the newly saved .json file'
        self.input_type['pif'] = opmod.workflow_item
        self.input_type['filename'] = opmod.workflow_item

    def run(self):
        p = self.inputs['pif']        
        dp = self.inputs['dirpath']
        fn = self.inputs['filename']
        if dp is None or fn is None or p is None:
            return
        if not os.path.splitext(fn)[1] == 'json':
            fn = fn+'.json'
        json_file = os.path.join(dp,fn)
        self.outputs['file_path'] = json_file
        pif.dump(p, open(json_file,'w'))

