import traceback
from PySide import QtCore

from ..operations.operation import Operation

class WfWorker(QtCore.QObject):
    """
    Container for storing and executing parts of a workflow,
    to be pushed onto QtCore.QThread(s) as needed.
    """
    
    finished = QtCore.Signal()
    opDone = QtCore.Signal(str,Operation)

    def __init__(self,to_run=None,parent=None):
        super(WfWorker,self).__init__(parent)
        self.to_run = to_run

    def work(self):
        try:
            for itm in self.to_run:
                # run and update the Operation in this TreeItem
                op = itm.data
                op.run()
                self.opDone.emit(itm.tag(),op)
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


