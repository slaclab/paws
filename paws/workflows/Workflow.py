from __future__ import print_function
import copy

class Workflow(object):
    """Workflows use PAWS Operations and Plugins to do useful things."""

    def __init__(self,inputs,outputs):
        super(Workflow,self).__init__()

        self.log_file = None
        self.message_callback = self.tagged_print
        self.stop_flag = False

        self.inputs = copy.deepcopy(inputs)
        self.outputs = copy.deepcopy(outputs)
        self.input_doc = dict.fromkeys(self.inputs.keys())
        self.output_doc = dict.fromkeys(self.outputs.keys())

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

