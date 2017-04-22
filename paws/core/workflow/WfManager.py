from functools import partial
from collections import OrderedDict
import copy

from PySide import QtCore

from ..plugins.PawsPlugin import PawsPlugin
from ..plugins.WorkflowPlugin import WorkflowPlugin
from .Workflow import Workflow
from ..operations.Operation import Operation        
from ..operations import optools        
# TODO: consider migrating threading to a ThreadPool 

class WfManager(QtCore.QObject):
    """
    Manager for paws Workflows. 
    Stores a list of Workflow objects, performs operations on them.
    """

    def __init__(self,plugin_manager,qapp_reference):
        self.workflows = OrderedDict() 
        self.appref = qapp_reference 
        self.plugman = plugin_manager
        self._n_threads = QtCore.QThread.idealThreadCount()
        # TODO: get more wf_threads working
        self._n_wf_threads = 1
        self._wf_threads = dict.fromkeys(range(self._n_threads)[:self._n_wf_threads]) 
        #self._wf_threads = dict.fromkeys(range(self._n_threads)) 
        self.logmethod = None
        super(WfManager,self).__init__()

    # this signal should emit the name (self.workflows dict key) of the workflow that finished.
    # used to signal the gui to update the "Run" button.
    wfdone = QtCore.Signal(str)

    @QtCore.Slot(str)
    def run_wf(self,wfname):
        self.workflows[wfname].run_wf()

    @QtCore.Slot(str)
    def stop_wf(self,wfname):
        self.workflows[wfname].stop_wf()

    @QtCore.Slot(str)
    def finish_wf(self,wfname):
        self.wfdone.emit(wfname)

    def auto_name(self,wfname):
        """
        Generate the next unique workflow name by appending '_x',
        where x is a minimal nonnegative integer.
        """
        goodname = False
        prefix = wfname
        idx = 1
        while not goodname:
            if not wfname in self.workflows.keys():
                goodname = True
            else:
                wfname = prefix+'_{}'.format(idx)
                idx += 1
        return wfname 

    def finish_thread(self,th_idx):
        #print 'finishing thread {}'.format(th_idx)
        self.appref.processEvents()
        self._wf_threads[th_idx] = None

    def register_thread(self,th_idx,th):
        #print 'saving thread {}'.format(th_idx)
        self._wf_threads[th_idx] = th

    def wait_for_thread(self,th_idx):
        """Wait for the thread at self._wf_threads[th_idx] to be finished"""
        #print 'waiting for thread {}'.format(th_idx)
        # when waiting for a thread to execute something,
        # best processEvents() to ensure that the application has a chance
        # to prepare the thing that will be executed
        self.appref.processEvents()
        done = False
        interval = 1
        wait_iter = 0
        total_wait = 0
        while not done:
            #if wait_iter > 0:
            #    print '{}... still waiting for thread {} for {}ms'.format(wait_iter,th_idx,total_wait)
            done = True
            if self._wf_threads[th_idx] is not None:
                if not self._wf_threads[th_idx].isFinished():
                    done = False
                if not done:
                    if interval <= float(total_wait)*0.01 and interval <= 100:
                        interval = interval * 10
                    self.loopwait(interval)
                    wait_iter += 1
                    total_wait += interval

    def next_available_thread(self):
        for idx,th in self._wf_threads.items():
            if not th:
                #print '[{}] found available thread {}'.format(__name__,idx)
                return idx
        # if none found, wait for first thread in self.wfman.wf_threads 
        self.wait_for_thread(0)
        #print '[{}] falling back on thread 0'.format(__name__)
        return 0

    def wait_for_threads(self):
        """Wait for all workflow execution threads to finish"""
        for idx,th in self._wf_threads.items():
            self.wait_for_thread(idx)

    def loopwait(self,interval):
        """
        Create an event loop to delay some time without busywaiting.
        Time interval is specified in milliseconds.
        """
        l = QtCore.QEventLoop()
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.timeout.connect(l.quit)
        t.start(interval)
        l.exec_()
        # processEvents() to continue the main event loop while waiting.
        self.appref.processEvents()

    def n_wf(self):
        return len(self.workflows)

    def write_log(self,msg):
        if self.logmethod:
            self.logmethod(msg)
        else:
            print(msg)

    def wf_threads(self):
        return self._wf_threads

    def add_wf(self,wfname):
        """
        Add a workflow to self.workflows, with key specified by wfname.
        If wfname is not unique (i.e. a workflow with that name already exists),
        this method will overwrite the existing workflow with a new one.
        """
        wf = Workflow(self)
        wf.exec_finished.connect( partial(self.finish_wf,wfname) )
        wf.wf_updated.connect( partial(self.plugman.update_plugin,wfname) )
        #wf.setParent(self)
        self.workflows[wfname] = wf
        # for every new workflow, add a plugin 
        wf_pgin = WorkflowPlugin()
        wf_pgin.inputs['workflow'] = self.workflows[wfname] 
        wf_pgin.start()
        self.plugman.add_plugin(wfname,wf_pgin)

    def load_from_dict(self,wfname,opman,opdict):
        """
        Create a workflow with name (self.workflows dict key) wfname.
        If wfname is not unique, self.workflows[wfname] is overwritten.
        Input opdict specifies operation setup,
        where each item in opdict provides enough information
        to get and set inputs for an Operation from OpManager opman.
        """
        self.add_wf(wfname)
        for uri, op_setup in opdict.items():
            op = self.build_op_from_dict(op_setup,opman)
            if op is None or not isinstance(op,Operation):
                self.write_log('Could not build Operation {} from \n{}\n-- skipping.'.format(uri,op_setup))
            else: 
                self.workflows[wfname].add_op(uri,op)
        # the wf_updated signal for this workflow is expected 
        # to be connected to the plugin manager at this point.
        # See WfManager.add_wf(). 
        self.workflows[wfname].wf_updated.emit()

    def op_setup_dict(self,op):
        op_mod = op.__module__[op.__module__.find('operations'):]
        op_mod = op_mod[op_mod.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_mod
        inp_dct = OrderedDict() 
        for name in op.inputs.keys():
            il = op.input_locator[name]
            inp_dct[name] = {'src':copy.copy(il.src),'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct[optools.inputs_tag] = inp_dct 
        return dct

    def build_op_from_dict(self,op_setup,opman):
        op_uri = op_setup['op_module']
        op = opman.get_data_from_uri(op_uri)
        if issubclass(op,Operation):
            op = op()
            op.load_defaults()
            il_setup_dict = op_setup[optools.inputs_tag]
            for name in op.inputs.keys():
                if name in il_setup_dict.keys():
                    src = il_setup_dict[name]['src']
                    #if 'tp' in il_setup_dict[name].keys():
                    tp = il_setup_dict[name]['tp']
                    val = il_setup_dict[name]['val']
                    if tp in optools.invalid_types[src]:
                        il = optools.InputLocator(src,optools.none_type,None)
                    else:
                        il = optools.InputLocator(src,tp,val)
                    op.input_locator[name] = il
                    # dereference any existing inputs
                    # LAP: commented out bc it should be handled in op.load_defaults()
                    #op.inputs[name] = None
            return op
        else:
            return None


