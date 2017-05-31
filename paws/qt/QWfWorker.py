from __future__ import print_function
import traceback
from PySide import QtCore

from ..core.operations.Operation import Operation

class QWfWorker(QtCore.QObject):
    """
    Container for storing and executing parts of a workflow,
    to be pushed onto QtCore.QThread(s) as needed.
    """
    
    #finished = QtCore.Signal()
    opDone = QtCore.Signal(str,Operation)
    wfDone = QtCore.Signal()

    def __init__(self,op_dict=None,parent_QObject=None):
        super(QWfWorker,self).__init__(parent_QObject)
        self.op_dict = op_dict 

    def work(self):
        try:
            for op_tag,op in self.op_dict.items():
                #try:
                    op.run()
                    self.opDone.emit(op_tag,op)
                #except Exception as ex:
                #    print '[{}] crashed with {}'.format(__name__,ex.message)
        except Exception as ex:
            # TODO: Deliver this exception to the user gracefully 
            tb = traceback.format_exc()
            msg = str('Error encountered during execution. \n'
                + 'Error message: {} \n'.format(ex.message) 
                + 'Stack trace: {}'.format(tb)) 
            print(msg)
            #raise ex
        self.wfDone.emit()


