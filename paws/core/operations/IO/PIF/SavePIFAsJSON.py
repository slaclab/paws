import os

from pypif import pif
import pypif.obj as pifobj 

from ... import Operation as opmod 
from ...Operation import Operation
        
class SavePIFAsJSON(Operation):
    """
    Take a pypif.obj.System object and save it on the local filesystem in .json format
    """

    def __init__(self):
        input_names = ['pif','dirpath','filename']
        output_names = ['response']
        super(SavePIFAsJSON,self).__init__(input_names,output_names)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['dirpath'] = 'Path to system directory where .json file will be created' 
        self.input_doc['filename'] = 'Name of the .json file to be created. '\
        'The .json extension is appended automatically if not provided.' 
        self.input_src['pif'] = opmod.wf_input
        self.input_src['dirpath'] = opmod.fs_input
        self.input_src['filename'] = opmod.wf_input
        self.input_type['pif'] = opmod.ref_type
        self.input_type['dirpath'] = opmod.path_type
        self.input_type['filename'] = opmod.ref_type

    def run(self):
        p = self.inputs['pif']        
        dp = self.inputs['dirpath']
        fn = self.inputs['filename']+'.json'
        #if not os.path.splitext(fn)[1] == 'json':
        #    fn = fn+'.json'
        json_file = os.path.join(dp,fn)
        pif.dump(p, open(json_file,'w'))

