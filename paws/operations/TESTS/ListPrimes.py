from collections import OrderedDict

from ..Operation import Operation

inputs = OrderedDict(n_primes=10)
outputs = OrderedDict(primes_list=[])

class ListPrimes(Operation):
    """Makes a list of prime numbers in increasing order"""

    def __init__(self):
        super(ListPrimes,self).__init__(inputs,outputs) 
        self.input_doc['n_primes'] = 'number of primes to output'
        self.output_doc['primes_list'] = 'list of prime numbers'
    
    def run(self):
        np = self.inputs['n_primes']
        pl = self.outputs['primes_list'] 
        npfound = 0
        x = 2
        while npfound < np:
            divs = [p for p in pl if x%p == 0]
            if not divs:
                npfound += 1 
                pl.append(x)
            x += 1
        return self.outputs

