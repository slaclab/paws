from collections import OrderedDict

from ... import Operation as op
from ...Operation import Operation

class ReadNPSynthRecipe(Operation):
    """
    Read in a text file describing nanoparticle synthesis parameters.
    Package the description in a dict. 
    """
    
    def __init__(self):
        input_names = ['recipe_file']
        output_names = ['recipe_dict']
        super(ReadNPSynthRecipe,self).__init__(input_names,output_names)
        self.input_doc['recipe_file'] = 'plain text file describing a synthesis recipe'
        self.input_src['recipe_file'] = op.fs_input
        self.input_type['recipe_file'] = op.path_type
        self.output_doc['recipe_dict'] = 'dict describing the synthesis recipe'

    def run(self):
        fpath = self.inputs['recipe_file']
        rdict = OrderedDict()
        ln = 0
        for line in open(fpath,'r'):
            ln += 1
            rdict[str(ln)] = line
        self.outputs['recipe_dict'] = rdict 

