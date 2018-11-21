from __future__ import print_function
from collections import OrderedDict
import copy
from threading import Condition

class Operation(object):
    """Class template for implementing paws operations"""

    def __init__(self,inputs,outputs):
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 
        self.message_callback = self.tagged_print 
        self.data_callback = None 

        # this lock and flag is used to stop long-running Operations.
        # another process can obtain the lock and set the stop_flag,
        # and then the long-running operation should check the flag's value
        # to decide whether or not to stop.
        self.stop_lock = Condition()
        self.stop_flag = False

    def __getitem__(self,key):
        return self.__dict__[key]

    def __setitem__(self,key,data):
        self.__dict__[key] = data

    def keys(self):
        #return self.__dict__.keys()
        return['inputs','outputs']

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def run_with(self,**kwargs):
        """Run the Operation with keyword arguments substituted for the inputs.

        Any keyword arguments that match the Operation.inputs keys
        are loaded into the Operation.inputs before calling Operation.run().
        All relevant results are stored in Operation.outputs.
        """
        for k in kwargs.keys():
            if not k in self.inputs:
                raise ValueError('Input {} is not valid for Operation {}'.format(k,type(self).__name__))
        self.inputs.update(kwargs)
        return self.run() 

    def run(self):
        """Run the Operation.

        All input data should be specified in Operation.inputs.
        All relevant results should be stored in Operation.outputs.
        """
        pass

    def stop(self):
        with self.stop_lock:
            self.stop_flag = True

    def build_clone(self):
        """Clone the Operation"""
        new_op = self.clone()
        new_op.inputs = copy.deepcopy(self.inputs)
        new_op.outputs = copy.deepcopy(self.outputs)
        return new_op

    @classmethod
    def clone(cls):
        # NOTE: this assumes the subclass constructor 
        # will have default arguments available
        return cls()

    def set_input(self,input_name,val):
        self.inputs[input_name] = val    

    def description(self):
        """Provide a string describing the Operation."""
        return type(self).__name__+": an Operation for PAWS"

