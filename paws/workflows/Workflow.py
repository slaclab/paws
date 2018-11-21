from __future__ import print_function
from collections import OrderedDict
import copy
from functools import partial

from ..pawstools import DictTree 

class Workflow(DictTree):
    """Workflow built from paws Operations, with DictTree interface."""

    def __init__(self,inputs,outputs):
        super(Workflow,self).__init__()

        # TODO: get the proper module_path for the subclasses
        self._module_path = __name__

        self.operations = self._root
        self.ops_enabled = OrderedDict() 
        self.log_file = None
        self.message_callback = self.tagged_print
        self.data_callback = self.set_data
        self.stop_flag = False

        self.declare_inputs(copy.deepcopy(inputs))
        self.declare_outputs(copy.deepcopy(outputs))


    def declare_inputs(self,inputs):
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 

    def declare_outputs(self,outputs):
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 

    def add_operations(self,**kwargs):
        for op_name, op in kwargs.items():
            self.add_operation(op_name,op)

    def add_operation(self,op_name,op):
        """Name and add an Operation to the Workflow.
    
        If `op_name` is not unique, 
        the existing Operation is overwritten.
    
        Parameters
        ----------
        op_name : str
            name to give to the new Operation 
        """
        #op.message_callback = self.message_callback
        op.data_callback = partial(self.set_op_item,op_name)
        self.ops_enabled[op_name] = True
        self.set_data(op_name,op)

    def tagged_print(self,msg):
        msg = '[{}] {}'.format(type(self).__name__,msg)  
        print(msg)
        if self.log_file:
            f = open(self.log_file,'a')
            f.write(msg+os.linesep)
            f.close()

    def set_log_file(self,file_path=None):
        if not file_path:
            suffix = 0
            default_file = '{}_{}.log'.format(type(self).__name__,suffix)
            file_path = os.path.join(pawstools.paws_scratch_dir,default_file)
            while os.path.exists(file_path):
                pth,ext = os.path.splitext(file_path)
                file_path = pth+'_{}'.format(suffix)+ext
                suffix += 1
        if file_path == self.log_file:
            return
        open(file_path,'a').close()
        self.message_callback('workflow log file: {}'.format(file_path))
        self.log_file = file_path 

    def set_op_inputs(self,op_name,**kwargs):
        for input_name,val in kwargs.items():
            self.set_op_input(op_name,input_name,val)

    def set_op_input(self,op_name,input_name,val):
        #if not op_name in self.operations:
        #    raise KeyError('operation name {} does not exist'.format(op_name))
        #if not input_name in self.operations[op_name].inputs:
        #    raise KeyError('input name {} does not exist for operation {}'
        #    .format(input_name,op_name))
        itm_key = op_name+'.inputs.'+input_name 
        self.verify_keys([itm_key])
        self.set_data(itm_key,val)

    def set_op_item(self,op_name,item_key,item_data):
        """Subroutine for use with functools.partial for callbacks"""
        full_key = op_name+'.'+item_key
        self.set_data(full_key,item_data)

    def verify_keys(self,keys):
        for k in keys:
            kparts = k.split('.')
            # check only the first three parts of the key:
            # things should be documented to that depth
            if len(kparts) > 3: kparts = kparts[:3]
            k_check = kparts.pop(0)
            for subk in kparts:
                k_check += '.' + subk
            if not k_check in self.keys():
                raise KeyError('Workflow item key {} does not exist'.format(k_check))

    def set_inputs(self,**kwargs):
        for input_name,val in kwargs.items():
            self.inputs[input_name] = val

    #def set_input(self,input_name,val):
    #    """Set a value for Workflow items in self.input_map[`input_name`]"""
    #    r = self.input_map[input_name]
    #    for k in r:
    #        self.set_data(k,val)
    #        # Update the wf_item map so the value is loaded at runtime 
    #        #self.set_wf_item(k,val)

    #def get_output(self,output_name):
    #    out_map = self.outputs[output_name]
    #    if len(out_map) == 1:
    #        return self.get_data(out_map[0])
    #    else:
    #        return [self.get_data(k) for k in out_map]

    #def set_wf_item(self,wf_item_key,val):
    #    self.verify_keys([wf_item_key])
    #    self.op_inputs[wf_item_key] = val

    def run_with(self,**kwargs):
        """Run the Workflow with keyword arguments substituted for the inputs.

        Any keyword arguments that match the Workflow.inputs keys
        are loaded into the Workflow.inputs before calling Workflow.run().
        All relevant results are stored in Workflow.outputs.
        """
        for k in kwargs.keys():
            if not k in self.inputs:
                raise ValueError('Input {} is not valid for Workflow {}'.format(k,type(self).__name__))
        self.inputs.update(kwargs)
        return self.run() 

    def run(self):
        """Run the Workflow."""
        pass

    def stop(self):
        """Stop the Workflow and all of its Operations."""
        with self.stop_lock:
            self.stop_flag = True
        # TODO: revisit this after implementing workflow threading
        #for op_name,op in self.operations.items():
        #    op.stop()

    def build_clone(self):
        """Produce a clone of this Workflow."""
        new_wf = self.clone() 
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        # TODO: consider how to handle callbacks; mind threading 
        new_wf.message_callback = self.message_callback
        new_wf.data_callback = self.data_callback
        return new_wf

    def setup_dict(self):
        """Return a dict that describes the Workflow setup.""" 
        wf_dict = OrderedDict()
        wf_dict['WF_MODULE'] = self._module_path 
        wf_dict['INPUTS'] = copy.deepcopy(self.inputs)
    #    wf_dict['OUTPUTS'] = copy.deepcopy(self.outputs)
        return wf_dict

    @classmethod
    def clone(cls):
        return cls()

    def enable_ops(self,*args):
        for op_name in args:
            self.enable_op(op_name)

    def disable_ops(self,*args):
        for op_name in args:
            self.disable_op(op_name)

    def enable_op(self,op_name):
        self.set_op_enabled(op_name,True)

    def disable_op(self,op_name):
        self.set_op_enabled(op_name,False)

    def set_op_enabled(self,op_name,flag=True):
        self.ops_enabled[op_name] = flag 

