from collections import OrderedDict

import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(uid=None)
outputs=OrderedDict(pif=None)

class EmptyPif(Operation):
    """
    Make and empty pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        super(EmptyPif,self).__init__(inputs,outputs)
        self.input_doc['uid'] = 'text string to use as pif record uid'
        self.output_doc['pif'] = 'an empty pif object'

    def run(self):
        uid = self.inputs['uid']
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid
        main_sys.tags = ['EMPTY']
        self.outputs['pif'] = main_sys

