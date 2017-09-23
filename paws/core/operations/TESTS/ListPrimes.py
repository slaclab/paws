from .. import Operation as opmod 
from ..Operation import Operation

class ListPrimes(Operation):
    """Makes a list of prime numbers in increasing order"""

    def __init__(self):
        input_names = ['n_primes']
        output_names = ['primes_list']
        super(ListPrimes,self).__init__(input_names,output_names) 
        self.input_doc['n_primes'] = 'number of primes to output'
        self.output_doc['primes_list'] = 'list of prime numbers'
        self.inputs['n_primes'] = 10 
    
    def run(self):
        np = self.inputs['n_primes']
        pl = []
        npfound = 0
        x = 2
        while npfound < np:
            divs = [p for p in pl if x%p == 0]
            if not divs:
                npfound += 1 
                pl.append(x)
            x += 1
        self.outputs['primes_list'] = pl

