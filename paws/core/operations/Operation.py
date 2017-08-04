import abc
import re
from collections import OrderedDict

# Enumeration of valid types for workflow and plugin inputs
no_input = 0
filesystem_path = 1
workflow_item = 2
workflow_path = 3
plugin_item = 4
string_type = 5 
integer_type = 6
float_type = 7
bool_type = 8
valid_types = list([no_input,filesystem_path,workflow_item,workflow_path,
    plugin_item,string_type,integer_type,float_type,bool_type])
input_types = list(['none','filesystem path','workflow item','workflow path','plugin item',
    'string','integer','float','boolean'])

# tags for Operation inputs and outputs in Workflow(TreeModel)s
inputs_tag = 'inputs'
outputs_tag = 'outputs'

class InputLocator(object):
    """
    Objects of this class are used as containers for inputs to an Operation.
    They contain the information needed to find the relevant input data.
    After the data is loaded, it should be stored in InputLocator.data.
    """
    def __init__(self,tp=no_input,val=None):
        self.tp = tp
        self.val = val 
        self.data = None 

class Operation(object):
    """
    Class template for implementing paws operations.
    """

    def __init__(self,input_names,output_names):
        """
        The input_names and output_names (lists of strings)
        are used to specify names for the parameters 
        that will be used to perform the operation.
        These lists are used as keys to build dicts
        Operation.inputs and Operation.outputs.
        """
        self.inputs = OrderedDict()
        self.input_locator = OrderedDict() 
        self.outputs = OrderedDict() 
        self.input_doc = OrderedDict() 
        self.input_type = OrderedDict() 
        self.output_doc = OrderedDict() 
        # For each of the i/o names, assign to None 
        for name in input_names: 
            self.input_type[name] = no_input
            self.input_locator[name] = None 
            self.inputs[name] = None
            self.input_doc[name] = None
        for name in output_names: 
            self.outputs[name] = None
            self.output_doc[name] = None

    def __getitem__(self,key):
        if key == inputs_tag:
            return self.inputs
        elif key == outputs_tag:
            return self.outputs
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def __setitem__(self,key,data):
        if key == inputs_tag:
            self.inputs = data
        elif key == outputs_tag:
            self.outputs = data
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def keys(self):
        return [inputs_tag,outputs_tag]

    def load_defaults(self):
        """
        Set default types and values into the Operation.input_locators.
        This should be called only on a new and unmodified Operation,
        or else it will overwrite any inputs that have been set.
        """
        for name in self.inputs.keys():
            tp = no_input 
            val = None
            if not self.input_type[name] == no_input:
                tp = self.input_type[name]
                if self.inputs[name] is not None:
                    if isinstance(self.inputs[name],list):
                        val = [str(v) for v in self.inputs[name]]
                    else:
                        val = str(self.inputs[name])
            self.input_locator[name] = InputLocator(tp,val)
            # defaults are now packaged in InputLocators, so can be dereferenced from self.inputs. 
            #self.inputs[name] = None

    def run(self):
        """
        Operation.run() should use the Operation.inputs
        and set values for all of the items in Operation.outputs.
        """
        pass

    def description(self):
        """
        self.description() returns a string 
        documenting the input and output structure 
        and usage instructions for the Operation
        """
        return str(type(self).__name__+": "
        + self.doc_as_string()
        + "\n\n--- Inputs ---"
        + self.input_description() 
        + "\n\n--- Outputs ---"
        + self.output_description())

    def doc_as_string(self):
        if self.__doc__:
            return re.sub("\s\s+"," ",self.__doc__.replace('\n','')) 
        else:
            return "none"

    def input_description(self):
        a = ""
        for name in self.inputs.keys(): 
            if self.input_locator[name]:
                display_val = self.input_locator[name]
            else:
                display_val = self.inputs[name] 
            a = a + '\n\n'+parameter_doc(name,display_val,self.input_doc[name])
        return a

    def output_description(self):
        a = ""
        for name,val in self.outputs.items(): 
            a = a + '\n\n'+parameter_doc(name,val,self.output_doc[name])
        return a

def parameter_doc(name,value,doc):
    if isinstance(value, InputLocator):
        tp_str = input_types[value.tp]
        v_str = str(value.val)
        return "- name: {} \n- value: {} ({}) \n- doc: {}".format(name,v_str,tp_str,doc) 
    else:
        v_str = str(value)
        return "- name: {} \n- value: {} \n- doc: {}".format(name,v_str,doc) 
                
