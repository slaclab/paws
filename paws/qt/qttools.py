from __future__ import print_function 
from PySide import QtCore

class RunnableExecutor(QtCore.QRunnable):
    """
    QRunnable that handles execution of a QWorkflow
    """

    def __init__(self,wf):
        super(RunnableExecutor,self).__init__()
        self.wf = wf

    def run(self):
        self.wf.execute()

