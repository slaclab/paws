from __future__ import print_function
from collections import OrderedDict
import copy
import traceback
import time

from .Workflow import Workflow
from ..operations import Operation as op
from ..operations.Operation import Operation, Batch, Realtime        
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

    def __init__(self,plugin_manager):
        #super(WfManager,self).__init__()
        self.workflows = OrderedDict() 
        self.plugman = plugin_manager
        self.logmethod = print 

    #def __getitem__(self,key):
    #    if key in self.workflows.keys():
    #        return self.workflows[key]
    #    else:
    #        raise KeyError('[{}] WfManager does not recognize workflow name {}.'
    #        .format(__name__,key))

    def n_wf(self):
        return len(self.workflows)

    def write_log(self,msg):
        self.logmethod(msg)
        #if self.logmethod:
        #else:
        #    print('- '+pawstools.timestr()+': '+msg)

    def add_wf(self,wfname):
        """
        Add a workflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow()
        self.workflows[wfname] = wf

    def run_wf(self,wfname):
        """
        Serially execute the operations of WfManager.workflows[wfname].
        Uses optools.execution_stack() to determine execution order.
        """
        stk,diag = optools.execution_stack(self.workflows[wfname])
        for lst in stk:
            batch_flag = isinstance(self.workflows[wfname].get_data_from_uri(lst[0]),Batch)
            rt_flag = isinstance(self.workflows[wfname].get_data_from_uri(lst[0]),Realtime)
            if not any([batch_flag,rt_flag]):
                self.execute_serial(wfname,lst)
            elif batch_flag:
                self.execute_batch(wfname,lst[0],lst[1])
            elif rt_flag:
                self.execute_realtime(wfname,lst[0],lst[1])

    def execute_batch(self,wfname,batch_op_tag,batch_stk):
        batch_op = self.workflows[wfname].get_data_from_uri(batch_op_tag) 
        optools.load_inputs(batch_op,self.workflows[wfname],self.plugman)
        batch_op.run()
        self.workflows[wfname].set_item(batch_op_tag,batch_op)
        n_batch = len(batch_op.input_list())
        for i in range(n_batch):
            input_dict = batch_op.input_list()[i]
            for uri,val in input_dict.items():
                self.workflows[wfname].set_op_input_at_uri(uri,val)
            self.write_log( 'BATCH EXECUTION {} / {}'.format(i+1,n_batch) )
            for batch_lst in batch_stk:
                self.execute_serial(wfname,batch_lst)
            saved_items_dict = OrderedDict()
            for uri in batch_op.saved_items():
                # TODO # BUG: there is the chance for infinite recursion here
                # if the batch is asked to save an upstream item?
                save_data = copy.deepcopy(self.workflows[wfname].get_data_from_uri(uri))
                save_dict = self.uri_to_embedded_dict(uri,save_data) 
                saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
            batch_op.output_list()[i] = saved_items_dict
            # TODO: set a more specific item here to save some tree update time?
            #self.workflows[wfname].set_item(batch_op_tag,batch_op)
            outputs_uri = batch_op_tag+'.'+op.outputs_tag+'.'+batch_op.batch_outputs_tag()+'.'+str(i)
            self.workflows[wfname].set_item(outputs_uri,saved_items_dict)

    def execute_realtime(self,wfname,rt_op_tag,rt_stk):
        rt_op = self.workflows[wfname].get_data_from_uri(rt_op_tag) 
        optools.load_inputs(rt_op,self.workflows[wfname],self.plugman)
        rt_op.run()
        self.workflows[wfname].set_item(rt_op_tag,rt_op)
        keep_running = True
        n_exec = 0
        wait_iter = 0
        while keep_running:
        ##TODO: ways to control the loop exit condition
            vals = rt_op.input_iter().next()
            if not None in vals:
                n_exec += 1
                wait_iter = 0
                inp_dict = OrderedDict( zip(rt_op.input_routes(), vals) )
                for uri,val in inp_dict.items():
                    self.workflows[wfname].set_op_input_at_uri(uri,val) 
                self.write_log( 'REALTIME EXECUTION {}'.format(n_exec))
                for rt_lst in rt_stk:
                    self.execute_serial(wfname,rt_lst)
                saved_items_dict = OrderedDict()
                for uri in rt_op.saved_items():
                    save_data = copy.deepcopy(self.workflows[wfname].get_data_from_uri(uri))
                    save_dict = self.uri_to_embedded_dict(uri,save_data) 
                    saved_items_dict = self.update_embedded_dict(saved_items_dict,save_dict)
                rt_op.output_list().append(saved_items_dict)
                output_uri = rt_op_tag+'.'+op.outputs_tag+'.'+rt_op.batch_outputs_tag()+'.'+str(i)
                self.workflows[wfname].set_item(output_uri,saved_items_dict)
            else:
                if wait_iter == 0:
                    self.write_log( 'Waiting for new inputs...' )
                wait_iter += 1 
                time.sleep(float(rt_op.delay())/1000.0)
            if wait_iter > 1000:
                self.write_log('Waited too long. Exiting...')
                keep_running = False

    def execute_serial(self,wfname,op_list):
        self.write_log('workflow {} running {}'.format(wfname,op_list))
        for op_tag in op_list: 
            op = self.workflows[wfname].get_data_from_uri(op_tag) 
            optools.load_inputs(op,self.workflows[wfname],self.plugman)
            try:
                op.run() 
            except Exception as ex:
                tb = traceback.format_exc()
                self.write_log(str('Operation {} of workflow {} threw an error. '
                + '\nMessage: {} \nTrace: {}').format(op_tag,wfname,ex.message,tb)) 
            self.workflows[wfname].set_item(op_tag,op)

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

    def load_from_dict(self,wfname,opman,opdict):
        """
        Create a workflow with name wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input opdict specifies operation setup,
        where each item in opdict provides enough information
        to get an Operation from OpManager opman
        and set up its Operation.input_locators.
        """
        self.add_wf(wfname)
        for opname, op_setup in opdict.items():
            op = self.build_op_from_dict(op_setup,opman)
            if isinstance(op,Operation):
                self.workflows[wfname].set_item(opname,op)
            else:
                self.write_log('[{}] Failed to load {}.'.format(uri))

    def op_setup_dict(self,op):
        op_mod = op.__module__[op.__module__.find('operations'):]
        op_mod = op_mod[op_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_mod
        inp_dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            inp_dct[name] = {'src':copy.copy(il.src),'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct[op.inputs_tag] = inp_dct 
        return dct

    def build_op_from_dict(self,op_setup,opman):
        op_uri = op_setup['op_module']
        op = opman.get_data_from_uri(op_uri)
        if issubclass(op,Operation):
            op = op()
            op.load_defaults()
            il_setup_dict = op_setup[op.inputs_tag]
            for name in op.inputs.keys():
                if name in il_setup_dict.keys():
                    src = il_setup_dict[name]['src']
                    #if 'tp' in il_setup_dict[name].keys():
                    tp = il_setup_dict[name]['tp']
                    val = il_setup_dict[name]['val']
                    if tp in op.invalid_types[src]:
                        il = op.InputLocator(src,op.none_type,None)
                    else:
                        il = op.InputLocator(src,tp,val)
                    op.input_locator[name] = il
                    # dereference any existing inputs
                    # LAP: commented out bc it should be handled in op.load_defaults()
                    #op.inputs[name] = None
            return op
        else:
            return None

    #def auto_name(self,wfname):
    #    """
    #    Generate the next unique workflow name by appending '_x',
    #    where x is a minimal nonnegative integer.
    #    """
    #    goodname = False
    #    prefix = wfname
    #    idx = 1
    #    while not goodname:
    #        if not wfname in self.workflows.keys():
    #            goodname = True
    #        else:
    #            wfname = prefix+'_{}'.format(idx)
    #            idx += 1
    #    return wfname 


