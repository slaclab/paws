import abc

class Operation(object):
    __metaclass__ = abc.ABCMeta
    """
    Metaclass template for implementing slacx operations.
    """

    @abc.abstractmethod
    def run(self):
        """Operation.run() should evaluate and return a dict of outputs."""
        pass

    @abc.abstractmethod
    def args(self):
        """
        Operation.args() should return a dict 
        containing the operation's inputs.  
        """
        pass

    @abc.abstractmethod
    def description(self):
        """
        self.description() should return a string 
        documenting the input and output structure of the Operation
        """
        pass

#    @abc.abstractmethod
#    def outputs(self):
#        raise NotImplementedError("subclasses of operation must implement outputs()")

