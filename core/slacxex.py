@staticmethod
def throw_specific_error(msg):
    msg = 'something specific happened: ' + msg
    raise Exception(msg)

class LazyCodeError(Exception):
    def __init__(self,msg):
        super(LazyCoderError,self).__init__(self,msg)

