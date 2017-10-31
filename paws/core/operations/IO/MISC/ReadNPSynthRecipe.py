from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

inputs=OrderedDict(file_path=None)
outputs=OrderedDict(recipe_dict=None)

class ReadNPSynthRecipe(Operation):
    """
    Read in a text file describing nanoparticle synthesis parameters.
    Package the recipe description in a dict. 
    """
    
    def __init__(self):
        super(ReadNPSynthRecipe,self).__init__(inputs,outputs)
        self.input_doc['file_path'] = 'plain text file describing a synthesis recipe'
        self.output_doc['recipe_dict'] = 'dict describing the synthesis recipe'

    def run(self):
        fpath = self.inputs['file_path']
        rdict = OrderedDict()
        ln = 0
        for line in open(fpath,'r'):
            ln += 1
            rdict[str(ln)] = line
        self.outputs['recipe_dict'] = rdict 

