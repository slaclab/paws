import abc
import re
from collections import OrderedDict

import optools

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
        The Operation.categories attribute is a list that indicates
        where the operation can be found in the OpManager tree.
        The Operation will appear one time for each category in the list.
        Subcategories are indicated by a ".", for example:
        self.categories = ['CAT1','CAT2.SUBCAT','CAT3'].
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
            self.input_src[name] = optools.no_input
            self.input_type[name] = optools.none_type
            self.input_locator[name] = None 
            self.inputs[name] = None
            self.input_doc[name] = None
        for name in output_names: 
            self.outputs[name] = None
            self.output_doc[name] = None
        # Set flags so that Batch and Realtime Operations
        # can be identified without having to import them.
        # Override these flags in Batch and Realtime,
        # and access them in optools
        self._batch_flag = False
        self._realtime_flag = False

    def __getitem__(self,key):
        if key == optools.inputs_tag:
            return self.inputs
        elif key == optools.outputs_tag:
            return self.outputs
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def __setitem__(self,key,data):
        if key == optools.inputs_tag:
            self.inputs = data
        elif key == optools.outputs_tag:
            self.outputs = data
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def keys(self):
        return [optools.inputs_tag,optools.outputs_tag]

    def load_defaults(self):
        for name in self.inputs.keys():
            src = optools.no_input
            tp = optools.none_type
            val = None
            if not self.input_src[name] == optools.no_input:
                src = self.input_src[name]
                #if (self.input_type[name] == optools.none_type
                #and src in [optools.wf_input,optools.fs_input,optools.batch_input,optools.plugin_input]):
                #    self.input_type[name] = optools.auto_type
                if (not self.input_type[name] == optools.none_type
                and not self.input_type[name] in optools.invalid_types[src]):
                    tp = self.input_type[name]
                    if self.inputs[name] is not None:
                        if isinstance(self.inputs[name],list):
                            val = [str(v) for v in self.inputs[name]]
                        else:
                            val = str(self.inputs[name])
            self.input_locator[name] = optools.InputLocator(src,tp,val)
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
        + "\n\n--- Input ---"
        + self.input_description() 
        + "\n\n--- Output ---"
        + self.output_description())

    def doc_as_string(self):
        if self.__doc__:
            return re.sub("\s\s+"," ",self.__doc__.replace('\n','')) 
        else:
            return "no documentation found"

    def input_description(self):
        a = ""
        inp_indx = 0
        for name in self.inputs.keys(): 
            if self.input_locator[name]:
                display_val = self.input_locator[name]
            else:
                display_val = self.inputs[name] 
            a = a + str("\n\nInput {}:\n".format(inp_indx) 
            + optools.parameter_doc(name,display_val,self.input_doc[name]))
            inp_indx += 1
        return a

    def output_description(self):
        a = ""
        out_indx = 0
        for name,val in self.outputs.items(): 
            a = a + str("\n\nOutput {}:\n".format(out_indx) 
            + optools.parameter_doc(name,val,self.output_doc[name]))
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


class Realtime(Batch):
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
        When there is no new set of inputs to run, should return None.
        """
        pass

    def delay(self):
        """
        Return the number of MILLIseconds to pause between iterations.
        Overload this method to change the pause time- default is 1 second.
        """
        return 1000


