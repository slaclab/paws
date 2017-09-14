from __future__ import print_function
from collections import OrderedDict
import copy
import traceback
import time

from .. import operations as ops
from .Workflow import Workflow
from ..operations import Operation as opmod
from ..operations.Operation import Operation#, Batch, Realtime        
from ..operations import optools
from .. import pawstools

class WfManager(object):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, 
    performs operations on them.
    Keeps a reference to a PluginManager
    for access to PawsPlugins.
    """

    def __init__(self):
        super(WfManager,self).__init__()
        self.workflows = OrderedDict() 
        self.logmethod = print 
        self.plugin_manager = None

    #def __getitem__(self,key):
    #    if key in self.workflows.keys():
    #        return self.workflows[key]
    #    else:
    #        raise KeyError('[{}] WfManager does not recognize workflow name {}.'
    #        .format(__name__,key))

    def get_op(self,wfname,opname):
        return self.workflows[wfname].get_data_from_uri(opname)

    def n_wf(self):
        return len(self.workflows)

    def write_log(self,msg):
        self.logmethod(msg)

    def add_wf(self,wfname):
        """
        Add a workflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow(self)
        if not wf.is_tag_valid(wfname): 
            raise pawstools.WfNameError(wf.tag_error_message(wfname))
        self.workflows[wfname] = wf

    def run_wf(self,wfname):
        """
        Call the execute() method of self.workflows[wfname]
        """
        self.workflows[wfname].execute()

    def uri_to_embedded_dict(self,uri,data=None):
        path = uri.split('.')
        endtag = path[-1]
        d = OrderedDict()
        d[endtag] = data
        for tag in path[:-1][::-1]:
            parent_d = OrderedDict()
            parent_d[tag] = d
            d = parent_d
        return d

    def update_embedded_dict(self,d,d_new):
        for k,v in d_new.items():
            if k in d.keys():
                if isinstance(d[k],dict) and isinstance(d_new[k],dict):
                    # embedded dicts: recurse
                    d[k] = self.update_embedded_dict(d[k],d_new[k])
                else:
                    # existing d[k] is not dict, and d_new[k] is dict: replace  
                    d[k] = d_new[k]
            else:
                # d[k] does not exist: insert
                d[k] = v
        return d

    def load_from_dict(self,wfname,wf_spec,op_manager):
        """
        Create a workflow with name wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input dict wf_spec specifies Workflow setup,
        including all operations, Workflow.inputs, and Workflow.outputs.
        """
        self.add_wf(wfname)
        wfin_spec = wf_spec.pop('WORKFLOW_INPUTS')
        wfout_spec = wf_spec.pop('WORKFLOW_OUTPUTS')
        for inpname,inpval in wfin_spec.items():
            self.workflows[wfname].connect_wf_input(inpname,inpval)
        for outname,outval in wfout_spec.items():
            self.workflows[wfname].connect_wf_output(outname,outval)
        for opname, op_setup in wf_spec.items():
            op = self.build_op_from_dict(op_setup,op_manager)
            if isinstance(op,Operation):
                self.workflows[wfname].set_item(opname,op)
            else:
                self.write_log('[{}] Failed to load {}.'.format(uri))

    def op_setup_dict(self,op):
        op_modulename = op.__module__[op.__module__.find('operations'):]
        op_modulename = op_modulename[op_modulename.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_modulename
        inp_dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            inp_dct[name] = {'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct[opmod.inputs_tag] = inp_dct 
        return dct

    def build_op_from_dict(self,op_setup,op_manager):
        op_uri = op_setup['op_module']
        if not ops.load_flags[op_uri]:
            op_manager.set_op_enabled(op_uri)
        op = op_manager.get_data_from_uri(op_uri)
        if issubclass(op,Operation):
            op = op()
            op.load_defaults()
            il_setup_dict = op_setup[opmod.inputs_tag]
            for name in op.inputs.keys():
                if name in il_setup_dict.keys():
                    tp = il_setup_dict[name]['tp']
                    val = il_setup_dict[name]['val']
                    op.input_locator[name] = opmod.InputLocator(tp,val) 
            return op
        else:
            return None

