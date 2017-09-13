"""
Template for developing operations for paws.
"""

import <modulepath.>Operation as opmod
from <modulepath.>Operation import Operation

# Replace <OperationName> with a SHORT operation title 
class <OperationName>(Operation):
    # Replace <Description of Operation> with a detailed description 
    """<Description of Operation>"""

    def __init__(self):
        """<Description of anything unusual performed during __init__()>"""
        # Name the inputs and outputs for your operation.
        input_names = ['<input_name_1>','<input_name_2>',<...>]
        output_names = ['<output_name_1>','<output_name_2>',<...>]
        # Replace <OperationName> with the Operation class name chosen above
        super(<OperationName>,self).__init__(input_names,output_names)
        # Provide a basic description for each of the inputs and outputs 
        self.input_doc['<input_name_1>'] = '<expectations for input 1>'
        self.input_doc['<input_name_2>'] = '<etc>'
        self.output_doc['<output_name_1>'] = '<description of output 1>'
        self.output_doc['<output_name_2>'] = '<etc>'
        # OPTIONAL: set default types for the inputs.
        # Valid types:
        #   opmod.no_input: 
        #       The Workflow ignores this input.
        #   opmod.auto_type: 
        #       The Workflow uses this object as-referenced. 
        #   opmod.workflow_item: 
        #       The Workflow interprets the input 
        #       as the address of a piece of data 
        #       that appeared upstream in the workflow: 
        #       typically 'some_op.outputs.some_output' or similar.
        #       inputs of this type are used to determine
        #       the order of Operations for the Workflow.
        #   opmod.entire_workflow:
        #       The Workflow interprets this input
        #       as the name of another Workflow in the WfManager.
        #       This is useful for Operations that 
        #       control the execution of Workflows,
        #       such as batch or real-time execution controllers. 
        #   opmod.plugin_input:
        #       The Workflow interprets the input
        #       as the address of a piece of data
        #       presented by a PawsPlugin in the PluginManager.
        #       Typically 'some_plugin.some_thing' or similar.
        self.input_type['<input_name_1>'] = <opmod.some_source>
        self.input_type['<input_name_2>'] = <etc>
        
    # Write a run() function for this Operation.
    def run(self):
        """<Optional extra docstring for run()>"""
        # Optional- create references in the local namespace for cleaner code.
        <inp1> = self.inputs['<input_name_1>']
        <inp2> = self.inputs['<input_name_2>']
        <etc>
        # Perform the computation
        < ... >
        # Save the output
        self.outputs['<output_name_1>'] = <computed_value_1>
        self.outputs['<output_name_2>'] = <etc>

