import abc
import re
from collections import OrderedDict

# constants used for enumerative types etc
# tags for inputs and outputs TreeItems    
inputs_tag = 'inputs'
outputs_tag = 'outputs'

# Declarations of valid sources and types for workflow and plugin inputs
##### TODO: the following but gracefully
no_input = 0
text_input = 1
fs_input = 2
wf_input = 3
plugin_input = 4
batch_input = 5 
valid_sources = [no_input,text_input,fs_input,wf_input,plugin_input,batch_input]
input_sources = ['none','text','filesystem','workflow','plugins','batch'] 

none_type = 0
str_type = 1
int_type = 2
float_type = 3
bool_type = 4
ref_type = 5
path_type = 6
auto_type = 7
valid_types = [none_type,str_type,int_type,float_type,bool_type,ref_type,path_type,auto_type]
input_types = ['none','string','integer','float','boolean','reference','path','auto']

invalid_types = {}                
invalid_types[no_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type,auto_type]
invalid_types[text_input] = [ref_type,path_type,auto_type]
invalid_types[fs_input] = [str_type,int_type,float_type,bool_type,ref_type,auto_type]
invalid_types[wf_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[plugin_input] = [str_type,int_type,float_type,bool_type,auto_type]
invalid_types[batch_input] = [str_type,int_type,float_type,bool_type,ref_type,path_type]

class InputLocator(object):
    """
    Objects of this class are used as containers for inputs to an Operation.
    They contain the information needed to find the relevant input data.
    After the data is loaded, it should be stored in InputLocator.data.
    """
    def __init__(self,src=no_input,tp=none_type,val=None):
        self.src = src
        self.tp = tp
        self.val = val 
        self.data = None 

def parameter_doc(name,value,doc):
    if isinstance(value, InputLocator):
        src_str = input_sources[value.src]
        tp_str = input_types[value.tp]
        v_str = str(value.val)
        return "- name: {} \n- source: {} \n- type: {} \n- value: {} \n- doc: {}".format(name,src_str,tp_str,v_str,doc) 
    else:
        tp_str = type(value).__name__
        return "- name: {} \n- type: {} \n- doc: {}".format(name,tp_str,doc) 

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
        self.input_src = OrderedDict() 
        self.input_type = OrderedDict() 
        self.output_doc = OrderedDict() 
        # For each of the i/o names, assign to None 
        for name in input_names: 
            self.input_src[name] = no_input
            self.input_type[name] = none_type
            self.input_locator[name] = None 
            self.inputs[name] = None
            self.input_doc[name] = None
        for name in output_names: 
            self.outputs[name] = None
            self.output_doc[name] = None
        # Set flags so that Batch and Realtime Operations
        # can be identified without having to import them.
        # Override these flags in Batch and Realtime.
        self._batch_flag = False
        self._realtime_flag = False

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
        for name in self.inputs.keys():
            src = no_input
            tp = none_type
            val = None
            if not self.input_src[name] == no_input:
                src = self.input_src[name]
                #if (self.input_type[name] == none_type
                #and src in [wf_input,fs_input,batch_input,plugin_input]):
                #    self.input_type[name] = auto_type
                if (not self.input_type[name] == none_type
                and not self.input_type[name] in invalid_types[src]):
                    tp = self.input_type[name]
                    if self.inputs[name] is not None:
                        if isinstance(self.inputs[name],list):
                            val = [str(v) for v in self.inputs[name]]
                        else:
                            val = str(self.inputs[name])
            self.input_locator[name] = InputLocator(src,tp,val)
            # defaults are now packaged in InputLocators, so can be dereferenced from self.inputs. 
            self.inputs[name] = None

    def run(self):
        """
        Operation.run() should use all of the items in Operation.inputs
        and set values for all of the items in Operation.outputs.
        """
        pass

    def description(self):
        """
        self.description() returns a string 
        documenting the input and output structure 
        and usage instructions for the Operation
        """
        return str(
        "Operation description: "
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
        inp_indx = 0
        for name in self.inputs.keys(): 
            if self.input_locator[name]:
                display_val = self.input_locator[name]
            else:
                display_val = self.inputs[name] 
            a = a + str("\n\nInput {}:\n".format(inp_indx) 
            + parameter_doc(name,display_val,self.input_doc[name]))
            inp_indx += 1
        return a

    def output_description(self):
        a = ""
        out_indx = 0
        for name,val in self.outputs.items(): 
            a = a + str("\n\nOutput {}:\n".format(out_indx) 
            + parameter_doc(name,val,self.output_doc[name]))
            out_indx += 1
        return a
                
class Batch(Operation):
    __metaclass__ = abc.ABCMeta
    """
    Class template for implementing batch execution operations.
    """
    def __init__(self,input_names,output_names):
        super(Batch,self).__init__(input_names,output_names)
        # Override Operation._realtime_flag
        # so Batch can be identified without importing
        self._batch_flag = True


    @abc.abstractmethod
    def output_list(self):
        """
        Produce a list of OrderedDicts representing the outputs for each batch input.
        Each OrderedDict should be populated with [output_uri:output_value] pairs.
        """
        pass

    @abc.abstractmethod
    def input_list(self):
        """
        Produce a list of OrderedDicts representing each set of inputs for the Batch to run.
        Each OrderedDict should be populated with [input_uri:input_value] pairs.
        """
        pass

    @abc.abstractmethod
    def input_routes(self):
        """
        Produce a list of the input routes used by the Batch,
        in the same order as each of the OrderedDicts 
        provided by Batch.input_list().
        """
        pass

    @abc.abstractmethod
    def batch_outputs_tag(self):
        """
        Return the output name (one of the self.outputs.keys()) 
        that indicates where the batch outputs should be stored. 
        """
        pass
    
    @abc.abstractmethod
    def saved_items(self):
        """
        Return a list of items (as workflow uris) 
        to be saved after each execution.
        """
        pass 

    @abc.abstractmethod
    def set_batch_ops(self,wf=None):
        """
        Set enough information in this Operation's inputs
        so that self.batch_ops() returns the correct
        list of operations to be run under the batch.
        Takes a Workflow as optional second argument,
        so that it can be used to call optools.locate_input()
        """
        pass

    @abc.abstractmethod
    def set_input_routes(self,wf=None):
        """
        Set enough information in this Operation's inputs
        so that self.input_routes() returns the correct
        list of workflow uris where the batch will set its inputs 
        Takes a Workflow as optional second argument,
        so that it can be used to call optools.locate_input()
        """
        pass


class Realtime(Operation):
    __metaclass__ = abc.ABCMeta
    """
    Class template for implementing realtime execution as an Operation.
    """
    def __init__(self,input_names,output_names):
        super(Realtime,self).__init__(input_names,output_names)
        # Override Operation._realtime_flag
        # so realtime Operation can be identified without importing
        self._batch_flag = False
        self._realtime_flag = True

    @abc.abstractmethod
    def input_iter(self):
        """
        Produce an iterator over OrderedDicts representing each set of inputs to run.
        Each dict should be populated with [input_uri:input_value] pairs.
        When there is no new set of inputs to run, input_iter().next() should return None.
        """
        pass

    @abc.abstractmethod
    def input_routes(self):
        """
        Produce a list of the input routes used by the Realtime,
        in the same order as each of the OrderedDicts 
        provided by Realtime.input_iter().
        """
        pass

    @abc.abstractmethod
    def output_list(self):
        """
        Produce a list of OrderedDicts representing the outputs for each Realtime input.
        Each OrderedDict should be populated with [output_uri:output_value] pairs.
        """
        pass

    @abc.abstractmethod
    def batch_outputs_tag(self):
        """
        Return the output name (one of the self.outputs.keys()) 
        that indicates where the outputs should be stored. 
        """
        pass

    @abc.abstractmethod
    def saved_items(self):
        """
        Return a list of items (as workflow uris) 
        to be saved after each execution.
        """
        pass 

    def delay(self):
        """
        Return the number of MILLIseconds to pause between iterations.
        Overload this method to change the pause time- default is 1 second.
        """
        return 1000


