from collections import OrderedDict
import os

from pypif import pif
import pypif.obj as pifobj 

from ...Operation import Operation

inputs=OrderedDict(
    pif=None,
    file_path=None)

outputs={}
        
class SavePIF(Operation):

    def __init__(self):
        super(SavePIF,self).__init__(inputs,outputs)
        self.input_doc['pif'] = 'A pypif.obj.System object or an array/list thereof'
        self.input_doc['file_path'] = 'Path where output (json) file will be created' 

    def run(self):
        p = self.inputs['pif']        
        fp = self.inputs['file_path']
        if not os.path.splitext(fp)[1] in ['.json','.JSON']:
            fp = fp+'.json'
        pif.dump(p, open(fp,'w'))

