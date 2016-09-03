import abc

class Operation(object):
    __metaclass__ = abc.ABCMeta
    """
    Metaclass template for implementing slacx operations.
    """

    def __init__(self,input_vars,output_vars):
        """
        The input_vars and output_vars (lists of strings)
        are used to specify names for the variables 
        that will be used to perform the operation.
        When loading the operation into the workspace,
        each name in input_vars becomes a variable 
        which must be assigned some value.
        Meanwhile, the output_vars specification is used to build
        workflow connections with results that are not yet computed.
        """
        self.inputs = {}
        self.outputs = {}
        # For each of the var names, assign to None 
        for name in input_vars: 
            self.inputs[name] = None
        for name in output_vars: 
            self.outputs[name] = None

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
    def inputs(self):
        """
        Operation.inputs() should return a dict 
        containing the operation's inputs.  
        """
        return self.inputs

    def set_input(self,inputname,source,value):
        self.inputs[inputname] = (source, value)

#    @abc.abstractmethod
    def outputs(self):
        """
        Operation.outputs() should return a dict 
        containing the operation's outputs.  
        """
        return self.outputs 

    @abc.abstractmethod
    def description(cls):
        """
        IMPORTANT: This is a class method. 
        It must be implemented with the with @classmethod decorator.
        self.description() should return a string 
        documenting the input and output structure 
        and usage instructions for the Operation
        """
        pass


