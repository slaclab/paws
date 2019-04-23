from collections import OrderedDict

from xrsdkit import system as xrsdsys
from xrsdkit.tools import primitives 
from xrsdkit.tools import profiler as xrsdprof
from xrsdkit.tools import ymltools as xrsdyml
from xrsdkit.models import predict as xrsdpred

from ..Operation import Operation 

inputs = OrderedDict(
    q_I=None,
    dI=None,
    sample_metadata={},
    fit_args={'error_weighted':True,'logI_weighted':True,'q_range':[0.,float('inf')]}
    )

outputs = OrderedDict(xrsd_system=None)

class XrsdkitProcess1d(Operation):

    def __init__(self):
        super(XrsdkitProcess1d,self).__init__(inputs,outputs)

    def run(self):
        q_I = self.inputs['q_I']
        feats = xrsdprof.profile_pattern(q_I[:,0],q_I[:,1])
        pred = xrsdpred.predict(feats)
        sys = xrsdpred.system_from_prediction(pred,q_I[:,0],q_I[:,1],
                sample_metadata=self.inputs['sample_metadata'],features=feats)
        errwtd = self.inputs['fit_args']['error_weighted']
        logwtd = self.inputs['fit_args']['logI_weighted']
        qrng = self.inputs['fit_args']['q_range']
        sys_opt = xrsdsys.fit(sys,q_I[:,0],q_I[:,1],dI=self.inputs['dI'],
                error_weighted=errwtd,logI_weighted=logwtd,q_range=qrng)
        self.outputs['xrsd_system'] = sys_opt
        return self.outputs

