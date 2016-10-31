from citrination_client import CitrinationClient
from pypif import pif
import pypif.obj as pifobj

from slacxop import Operation
import optools

class PackageNPSynthesisAsPif(Operation):
    """
    Take PIF-style Property objects 
    produced from a nanoparticle solution synthesis experiment 
    and package them in a PIF.
    """

    def __init__(self):
        input_names = ['pif_property_source','citrination_client']
        output_names = ['pif_record']
        super(PackageNPSynthesisAsPif,self).__init__(input_names,output_names)
        self.input_doc['pif_property_source'] = str('The uri in the operations tree ' 
            + 'that will point to the Property records produced for each measurement '
            + 'taken in a single nanoparticle synthesis experiment.'
            + 'It is expected that each of these Property objects will be produced '
            + 'individually from one execution of a workflow, ' 
            + 'and the set of all Property objects will be produced '
            + 'by running this workflow in batch mode over a set of input files.')
        self.input_doc['citrination_client'] = str('(optional): A citrination client object '
            + 'should be supplied if the product PIF intends to be shipped to a Citrination instance')
        self.output_doc['pif_record'] = str('A PIF object that will be built '
            + 'to include sequentially each of the Property objects in the batch.')
        self.categories = ['OUTPUT']
        self.input_src['pif_property_source'] = optools.op_input
        self.input_src['citrination_client'] = optools.op_input 
        
    # Write a run() function for this Operation.
    def run(self):
        p_src = self.inputs['pif_property_source']
        cit_cli = self.inputs['citrination_client']
        # Perform the computation
        pif_result = pifobj.System()
        # Save the output
        self.outputs['pif_record'] = pif_result

