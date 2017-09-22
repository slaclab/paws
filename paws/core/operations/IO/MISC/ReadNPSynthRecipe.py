from collections import OrderedDict

from ... import Operation as opmod 
from ...Operation import Operation

class ReadNPSynthRecipe(Operation):
    """
    Read in a text file describing nanoparticle synthesis parameters.
    Package the recipe description in a dict. 
    """
    
    def __init__(self):
        input_names = ['file_path']
        output_names = ['recipe_dict']
        super(ReadNPSynthRecipe,self).__init__(input_names,output_names)
        self.input_doc['file_path'] = 'plain text file describing a synthesis recipe'
        self.output_doc['recipe_dict'] = 'dict describing the synthesis recipe'

    def run(self):
        fpath = self.inputs['file_path']
        if fpath is None:
            return
        rdict = OrderedDict()
        ln = 0
        for line in open(fpath,'r'):
            ln += 1
            rdict[str(ln)] = line
        self.outputs['recipe_dict'] = rdict 

