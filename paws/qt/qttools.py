from PySide import QtCore

class RunnableExecutor(QtCore.QRunnable):
    """
    QRunnable that handles execution of an Operation
    """
    def __init__(self,op):
        self.op = op 
        super(RunnableExecutor,self).__init__()

    def run(self): 
        self.op.run()

