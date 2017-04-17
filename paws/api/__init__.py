"""Module defining the API for paws"""

from functools import partial

from PySide import QtCore

from ..core.operations.OpManager import OpManager 
from ..core.workflow.WfManager import WfManager 
from ..core.plugins.PluginManager import PluginManager 
from ..core.operations import optools

#class PawsAPI(QtCore.QObject):
class PawsAPI(object):
    """
    Objects of this class act as delegates to interact with a paws application.
    """

    def __init__(self,app_args):
        super(PawsAPI,self).__init__()
        self._app = core_app(app_args)
        #self._app = None 
        self._op_manager = OpManager()
        self._plugin_manager = PluginManager()
        self._wf_manager = WfManager(self._plugin_manager,self._app)
        self._current_wf_name = None 
        #print self.inspect_objects()
        #self.wf_exec_requested.connect(self._wf_manager.run_wf)
    
    #wf_exec_requested = QtCore.Signal(str)

    def add_wf(self,wfname):
        self._wf_manager.add_wf(wfname)
        if not self._current_wf_name:
            self.select_wf(wfname)
        #print self.inspect_objects()

    def select_wf(self,wfname):
        if wfname in self._wf_manager.workflows.keys():
            self._current_wf_name = wfname
        else:
            msg = str('requested workflow {} not found in {}'
            .format(wfname,self._wf_manager.workflows.keys()))
            raise ValueError(msg)

    def current_wf(self):
        if self._current_wf_name:
            return self._wf_manager.workflows[self._current_wf_name]    
        else:
            return None

    def get_wf(self,wfname=None):
        if wfname is None:
            return self.current_wf()
        else:
            return self._wf_manager.workflows[wfname]

    def enable_ops(self,*args):
        # TODO: operation enable/disable functionality
        pass
        #for opname in args:
        #    print 'enable {}'.format(opname)

    def add_op(self,op_tag,op_spec,wfname=None):
        wf = self.get_wf(wfname)
        # get the op referred to by op_spec
        itm,idx = self._op_manager.get_from_uri(op_spec)
        op = itm.data
        # instantiate with default inputs
        op = op()
        op.load_defaults()
        wf.add_op(op_tag,op)
        #print self.inspect_objects()

    def remove_op(self,op_tag,wfname=None):
        wf = self.get_wf(wfname)
        #print 'remove {}'.format(op_tag)
        rm_itm, rm_idx = wf.get_from_uri(op_tag)
        wf.remove_op(rm_idx)
        #self._app.processEvents()
        #print self.inspect_objects()

    def get_op(self,opname,wfname=None):
        wf = self.get_wf(wfname)
        itm,idx = wf.get_from_uri(opname)
        op = itm.data
        return op 

    def get_output(self,opname,output_name,wfname=None):
        op = self.get_op(opname,wfname)
        return op.outputs[output_name]

    def set_input(self,opname,input_name,wfname=None,**kwargs):
        op = self.get_op(opname,wfname) 
        src = op.input_locator[input_name].src
        tp = op.input_locator[input_name].tp
        val = op.input_locator[input_name].val
        if 'src' in kwargs:
            if kwargs['src'] in optools.input_sources:
                src = optools.valid_sources[ optools.input_sources.index(kwargs['src']) ]
            else:
                #TODO: error? warning?
                src = optools.no_input
        if 'tp' in kwargs:
            if kwargs['tp'] in optools.input_types:
                tp = optools.valid_types[ optools.input_types.index(kwargs['tp']) ]
            else:
                #TODO: error? warning?
                tp = optools.none_type
        if 'val' in kwargs:
            val = kwargs['val']
        il = optools.InputLocator(src,tp,val)
        op.input_locator[input_name] = il
        #print 'set input {} of {} to src: {}, tp: {}, val: {}'.format(
        #input_name,opname,src,tp,val)
        
    def execute(self,wfname=None):
        wf = self.get_wf(wfname)
        wf.run_wf()
        #print self.inspect_objects()

        #if wfname is None:
        #    wfname = self._current_wf_name
        #wf.exec_finished.connect(self._app.quit)

        #l = QtCore.QEventLoop()
        #t = QtCore.QTimer()
        #t.setSingleShot(True)
        #t.timeout.connect( partial(self.wf_exec_requested,wfname) )
        #t.start(0)
        #self._app.exec_()
        #l.exec_()
        # processEvents() to continue the main event loop while waiting.
        #self._wf_manager.wfdone.connect(self._app.quit)

        #self.wf_exec_requested.emit(self._current_wf_name)
        # self._app provides a QEventLoop to update data structures while workflow runs

        #self._wf_manager.run_wf(self._current_wf_name)
        #self.current_wf().run_wf()
        # set the application start signal to execute the workflow
        # set the workflow finished signal to quit the app

    #def stop(self):
    #    self._app.quit()

    def save_config(self):
        self._op_manager.save_config()

    def op_manager(self):
        """
        Get a reference to the operation manager 
        (paws.core.operations.OpManager.OpManager). 
        Intended for use by other interfaces, e.g. the GUI manager.
        """
        return self._op_manager
    
    def wf_manager(self):
        """
        Get a reference to the workflow manager 
        (paws.core.workflow.WfManager.WfManager). 
        Intended for use by other interfaces, e.g. the GUI manager.
        """
        return self._wf_manager

    def plugin_manager(self):
        """
        Get a reference to the plugin manager 
        (paws.core.plugins.PluginManager.PluginManager). 
        Intended for use by other interfaces, e.g. the GUI manager.
        """
        return self._plugin_manager

    def inspect_objects(self):
        """
        Use QObject.findChildren() to count references to child objects
        of the top-level paws resource managers.
        Return a report of the result as a string.
        """
        opman_children = self._op_manager.findChildren(QtCore.QObject)
        wfman_children = self._wf_manager.findChildren(QtCore.QObject)
        plugman_children = self._plugin_manager.findChildren(QtCore.QObject)
        rpt = str('paws QObject count:\n'
            + 'operations manager: {}\n{}...\n'.format(len(opman_children),opman_children)
            + 'plugins manager: {}\n{}\n'.format(len(plugman_children),plugman_children)
            + 'workflow manager: {}\n{}\n'.format(len(wfman_children),wfman_children))
        for wfname,wf in self._wf_manager.workflows.items():
            wf_children = wf.findChildren(QtCore.QObject)
            rpt += '\tworkflow {}: {}\n\t{}\n'.format(wfname,len(wf_children),wf_children)
        return rpt
        

def start(app_args=[]):
    """
    Instantiate and return a PawsAPI object. 

    paws.api.start() calls the PawsAPI constructor.

    :param app_args: arguments to pass to the 
    QApplication constructor within the PawsAPI constructor
    :type args: sequence
    :returns: a PawsAPI object
    :return type: paws.api.PawsAPI 
    """
    return PawsAPI(app_args)


def core_app(app_args=[]):
    """
    Return a reference to a new QCoreApplication or a currently running QApplication.
    
    Input arguments are passed to the QApplication constructor.
    If a RuntimeError is thrown,
    it is assumed that a QApplication is already running,
    and an attempt is made to return a reference to that QApplication.
    If that fails, this returns None.

    :param app_args: arguments to pass to the QApplication constructor
    :type args: sequence
    :returns: reference to a new or existing QCoreApplication
    :return type: PySide.QtCore.QCoreApplication or None
    """
    try:
        app = QtCore.QCoreApplication(app_args)
    except RuntimeError:
        try:
            app = QtCore.QCoreApplication.instance()
        except:
            app = None
    return app

