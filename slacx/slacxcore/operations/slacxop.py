import abc

import optools

class Operation(object):
    __metaclass__ = abc.ABCMeta
    """
    Abstract class template for implementing slacx operations.
    """

    def __init__(self,input_names,output_names):
        """
        The input_names and output_names (lists of strings)
        are used to specify names for the parameters 
        that will be used to perform the operation.
        When loading the operation into the workspace,
        each name in input_names becomes a variable 
        which must be assigned some value.
        Meanwhile, the output_names specification is used to build
        workflow connections with results that are not yet computed.
        The categories attribute is a list that indicates
        where the operation can be found in the OpManager tree.
        The Operation will be listed under each category in the list.
        Subcategories are indicated by a ".", for example:
        self.categories = ['CAT1','CAT2.SUBCAT','CAT3']
        """
        self.inputs = {}
        self.input_doc = {}
        self.outputs = {}
        self.output_doc = {}
        # For each of the var names, assign to None 
        for name in input_names: 
            self.inputs[name] = None
            self.input_doc[name] = None
        for name in output_names: 
            self.outputs[name] = None
            self.output_doc[name] = None
        # Set default category to be 'MISC'
        self.categories = ['MISC']

    def print_locals(self):
        # debug: print local namespace.
        print self.locals()

    @abc.abstractmethod
    def run(self):
        """
        Operation.run() should use all of the Operation.inputs
        and set values for all of the Operation.outputs.
        It is expected that the Operation will have values
        set for all items in inputs before calling run().
        """
        pass

#    @abc.abstractmethod
#    def inputs(self):
#        """
#        Operation.inputs() should return a dict 
#        containing the operation's inputs.  
#        """
#        return self.inputs

#    def set_input(self,inputname,source,value):
#        self.inputs[inputname] = (source, value)

#    @abc.abstractmethod
#    def outputs(self):
#        """
#        Operation.outputs() should return a dict 
#        containing the operation's outputs.  
#        """
#        return self.outputs 

    def description(self):
        """
        self.description() returns a string 
        documenting the input and output structure 
        and usage instructions for the Operation
        """
        return str(
        "Operation description: \n"
        + self.__doc__ 
        + "\n\nInputs: \n"
        + self.inputs_description()
        + "\nOutputs: \n"
        + self.outputs_description())

    def inputs_description(self):
        a = ""
        for name,val in self.inputs.items(): 
            a = a + optools.parameter_doc(name,val,self.input_doc[name]) + "\n"
        return a

    def outputs_description(self):
        a = ""
        for name,val in self.outputs.items(): 
            a = a + optools.parameter_doc(name,val,self.output_doc[name]) + "\n"
        return a

#    @abc.abstractmethod
#    def tag(self):
#        """
#        self.tag() should return a string 
#        containing a human-readable name for this operation.
#        """
#        pass

