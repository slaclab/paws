import traceback
from PySide import QtCore

from ..operations.Operation import Operation

class WfWorker(QtCore.QObject):
    """
    Container for storing and executing parts of a workflow,
    to be pushed onto QtCore.QThread(s) as needed.
    """
    
    #finished = QtCore.Signal()
    opDone = QtCore.Signal(str,Operation)

    def __init__(self,op_dict=None,parent_QObject=None):
        super(WfWorker,self).__init__(parent_QObject)
        self.op_dict = op_dict 

    def work(self):
        try:
            for op_tag,op in self.op_dict.items():
                # run and update the Operation in this TreeItem
                op.run()
                self.opDone.emit(op_tag,op)
            self.thread().quit()
        except Exception as ex:
            # TODO: Deliver this exception to the user gracefully 
            tb = traceback.format_exc()
            msg = str('Error encountered during execution. \n'
                + 'Error message: {} \n'.format(ex.message) 
                + 'Stack trace: {}'.format(tb)) 
            print msg
            self.thread().quit()
            raise ex


