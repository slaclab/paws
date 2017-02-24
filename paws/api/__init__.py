"""Module defining the API for paws"""

from PySide import QtCore

from paws.core.operations.op_manager import OpManager 
from paws.core.workflow.wf_manager import WfManager 
from paws.core.plugins.plugin_manager import PluginManager 
from paws.core.operations import optools

class PawsAPI(object):

    def __init__(self,app_args):
        super(PawsAPI,self).__init__()
        self._app = core_app(app_args)
        self._op_manager = OpManager()
        self._plugin_manager = PluginManager()
        self._wf_manager = WfManager(self._plugin_manager,self._app)
    
    def enable_ops(self,*args):
        for opname in args:
            print 'enable {}'.format(opname)

    def add_op(self,op_tag,op_spec):
        # get the op referred to by op_spec
        itm,idx = self._op_manager.get_from_uri(op_spec)
        op = itm.data
        # instantiate with default inputs
        op = op()
        op.load_defaults()
        # add it to the workflow manager, tagged with op_tag
        self._wf_manager.add_op(op_tag,op)

    def set_input(self,op_name,input_name,**kwargs):
        itm,idx = self._wf_manager.get_from_uri(op_name)
        op = itm.data
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
        print 'set input {} of {} to src: {}, tp: {}, val: {}'.format(
        input_name,op_name,src,tp,val)
        
    def execute(self):
        print 'execute...'
        self._wf_manager.run_wf()
        # set the application start signal to execute the workflow
        # set the workflow finished signal to quit the app
        #self._app.exec_()

    def stop(self):
        self._app.quit()

    def save_config(self):
        self._op_manager.save_config()

    # For low-level control, provide access to core objects
    def op_manager(self):
        return self._op_manager
    
    def wf_manager(self):
        return self._wf_manager

    def plugin_manager(self):
        return self._plugin_manager


def start(app_args=[]):
    """
    Instantiate and return PawsAPI object. 

    paws.api.start() calls the PawsAPI constructor.

    :param app_args: arguments to pass to the 
    QApplication constructor within the PawsAPI constructor
    :type args: sequence
    :returns: a PawsAPI 
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

