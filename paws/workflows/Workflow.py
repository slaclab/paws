from __future__ import print_function
import copy

class Workflow(object):
    """Workflows use PAWS Operations and Plugins to do useful things."""

    def __init__(self,inputs,outputs):
        super(Workflow,self).__init__()

        self.log_file = None
        self.message_callback = self.tagged_print
        self.stop_flag = False

        self.default_inputs = copy.deepcopy(inputs)
        self.default_outputs = copy.deepcopy(outputs)
        self.inputs = copy.deepcopy(inputs)
        self.outputs = copy.deepcopy(outputs)

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

    def run_with(self,**kwargs):
        """Run the Workflow with inputs specified by keyword arguments.

        When called, this method loads the default inputs and outputs into the Workflow,
        then updates the inputs with the keyword arguments,
        then returns a copy of the return value of the Workflow's run() function
        (often, the return value of run() will be the Workflow outputs).
        """
        for k in kwargs.keys():
            if not k in self.inputs:
                raise ValueError('Input {} is not valid for Workflow {}'.format(k,type(self).__name__))
        self.inputs = copy.deepcopy(self.default_inputs)
        self.outputs = copy.deepcopy(self.default_outputs)
        self.inputs.update(kwargs)
        return copy.deepcopy(self.run())

    def run(self):
        """Run the Workflow."""
        pass

    def stop(self):
        """Stop the Workflow and all of its Operations."""
        pass 
        #for op_name,op in self.operations.items():
        #    op.stop()

    def build_clone(self):
        """Produce a clone of this Workflow."""
        new_wf = self.clone() 
        new_wf.inputs = copy.deepcopy(self.inputs)
        new_wf.outputs = copy.deepcopy(self.outputs)
        new_wf.message_callback = self.message_callback
        return new_wf

    @classmethod
    def clone(cls):
        return cls()

