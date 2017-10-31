from __future__ import print_function
import abc
import re
from collections import OrderedDict
import copy

# Enumeration of valid types for workflow and plugin inputs
no_input = 0            # ensure the input is set to None 

basic_type = 1          # input is set by hand, 
                        # and is of a basic type
                        # that is easy to serialize 

workflow_item = 2       # the address (TreeModel uri)
                        # of an item in the workflow 

entire_workflow = 3     # the name of a Workflow
                        # in the current WfManager

plugin_item = 4         # the address (TreeModel uri)
                        # of an item in the PluginManager

runtime_type = 5        # input is generated and set during execution,
                        # and serialization should not be attempted


valid_types = [no_input,basic_type,workflow_item,entire_workflow,plugin_item,runtime_type]
input_types = ['none','basic','workflow item','entire workflow','plugin item','runtime']

class InputLocator(object):
    """
    Objects of this class are used as containers for inputs to an Operation.
    They contain the information needed to find the relevant input data.
    """
    def __init__(self,tp=no_input,val=None):
        self.tp = tp
        self.val = val 
        #self.data = None 

class Operation(object):
    """Class template for implementing paws operations"""

    def __init__(self,inputs,outputs):
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.input_locator = OrderedDict.fromkeys(self.inputs.keys())
        self.outputs = OrderedDict.fromkeys(self.outputs.keys()) 
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.input_type = OrderedDict.fromkeys(self.inputs.keys()) 
        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 
        for name in self.inputs.keys(): 
            self.input_type[name] = basic_type 
        self.message_callback = print
        self.data_callback = None 
    
    def __getitem__(self,key):
        if key == 'inputs':
            return self.inputs
        elif key == 'outputs':
            return self.outputs
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def __setitem__(self,key,data):
        if key == 'inputs':
            self.inputs = data
        elif key == 'outputs':
            self.outputs = data
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def keys(self):
        return ['inputs','outputs']

    def load_defaults(self):
        """
        Set default types and values into the Operation.input_locators.
        """
        for name in self.inputs.keys():
            tp = self.input_type[name]
            val = self.inputs[name]
            self.input_locator[name] = InputLocator(tp,val)

    def run(self):
        """
        Operation.run() should use the Operation.inputs
        and set values for all of the items in Operation.outputs.
        """
        pass

    @classmethod
    def clone(cls):
        return cls()

    def clone_op(self):
        """Clone the Operation.

        If this is used to provide a copy of the Operation
        for distributed execution, then it should be called 
        after all inputs have been loaded,
        with the exception of workflow items,
        e.g. after calling WfManager.prepare_wf().
        """
        new_op = self.clone()
        new_op.load_defaults()
        for nm,il in self.input_locator.items():
            new_il = InputLocator()
            new_il.tp = copy.copy(il.tp)
            new_il.val = copy.copy(il.val)
            if il.tp == entire_workflow:
                if self.inputs[nm]:
                    new_wf = self.inputs[nm].clone_wf()
                    new_op.inputs[nm] = new_wf 
            else: 
                # NOTE: have to implement __deepcopy__
                # for whatever the input is.
                new_op.inputs[nm] = copy.deepcopy(self.inputs[nm]) 
            new_op.input_locator[nm] = new_il
        #new_op.message_callback = self.message_callback
        #new_op.data_callback = self.data_callback
        return new_op

    def setup_dict(self):
        """Produce a dictionary fully describing the setup of the Operation.

        Returns
        -------
        dct : dict
            Dictionary specifying the module name and input setup 
            for the current state of the Operation
        """
        op_modulename = self.__module__[self.__module__.find('operations'):]
        op_modulename = op_modulename[op_modulename.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_modulename
        inp_dct = OrderedDict() 
        for nm,il in self.input_locator.items():
            inp_dct[nm] = {'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct['inputs'] = inp_dct 
        return dct
    
    def clear_outputs(self):
        for k,v in self.outputs.items():
            self.outputs[k] = None

    def description(self):
        """Provide a string describing the Operation.
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
            a = a + '\n\n'+self.parameter_doc(name,display_val,self.input_doc[name])
        return a

    def output_description(self):
        a = ""
        for name,val in self.outputs.items(): 
            a = a + '\n\n'+self.parameter_doc(name,val,self.output_doc[name])
        return a
    
    @staticmethod
    def parameter_doc(name,value,doc):
        if isinstance(value, InputLocator):
            tp_str = input_types[value.tp]
            v_str = str(value.val)
            return "- name: {} \n- value: {} ({}) \n- doc: {}".format(name,v_str,tp_str,doc) 
        else:
            v_str = str(value)
            return "- name: {} \n- value: {} \n- doc: {}".format(name,v_str,doc) 
                
