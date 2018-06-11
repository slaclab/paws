from __future__ import print_function
import abc
import re
from collections import OrderedDict
import copy

from .. import pawstools

class Operation(object):
    """Class template for implementing paws operations"""

    def __init__(self,inputs,outputs):
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 
        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 

        # input datatypes are used for typecasting,
        # for when values are set indirectly,
        # e.g. through a gui.
        # if an input is not likely to be set via gui,
        # e.g. if it is a complicated or duck-typed object, 
        # this should be left to None,
        # in which case gui applications should have some default behavior.
        self.input_datatype = OrderedDict.fromkeys(self.inputs.keys())

        self.message_callback = self.tagged_print 
        self.data_callback = None 
        self.stop_flag = False

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

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    def run(self):
        """
        Operation.run() should use the Operation.inputs
        and set values for all of the items in Operation.outputs.
        """
        pass

    def stop(self):
        self.stop_flag = True

    def get_outputs(self):
        return self.outputs

    @classmethod
    def clone(cls):
        return cls()

    def build_clone(self):
        """Clone the Operation"""
        return self.clone()

    def set_input(self,input_name,val):
        self.inputs[input_name] = val    

    def clear_outputs(self):
        for k,v in self.outputs.items():
            self.outputs[k] = None

    def description(self):
        """Provide a string describing the Operation."""
        return str(type(self).__name__+": "+ self.doc_as_string()

    def doc_as_string(self):
        if self.__doc__:
            return re.sub("\s\s+"," ",self.__doc__.replace('\n','')) 
        else:
            return "none"

