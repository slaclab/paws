from PySide import QtCore

class RunnableExecutor(QtCore.QRunnable,QtCore.QObject):
    """
    QRunnable that handles execution of an Operation
    """
    runStarted = QtCore.Signal()
    runFinished = QtCore.Signal()

    def __init__(self,wf,logmethod):
        super(RunnableExecutor,self).__init__()
        self.wf = wf
        self.logmethod = logmethod

    def run(self):
        #self.runStarted.emit() 
        self.wf.execute(self.logmethod)
        #self.runFinished.emit()

