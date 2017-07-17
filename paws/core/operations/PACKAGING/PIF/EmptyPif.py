import pypif.obj as pifobj

from ... import Operation as op
from ...Operation import Operation

class EmptyPif(Operation):
    """
    Package results from nanoparticle solution synthesis into a pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['uid_prefix','date_time','t_utc']
        output_names = ['pif']
        super(EmptyPif,self).__init__(input_names,output_names)
        self.input_doc['uid_prefix'] = 'text string to prepend to pif uid (pif uid = uid_prefix+t_utc)'
        self.input_doc['date_time'] = 'string date/time for pif record tags'
        self.input_doc['t_utc'] = 'time of record creation in utc'
        self.output_doc['pif'] = 'an empty pif object'
        self.input_src['uid_prefix'] = op.text_input
        self.input_src['date_time'] = op.wf_input
        self.input_src['t_utc'] = op.wf_input
        self.input_type['uid_prefix'] = op.str_type
        self.input_type['date_time'] = op.ref_type
        self.input_type['t_utc'] = op.ref_type

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = uid_pre+'_'+str(int(t_utc))
        # TODO: Quantity information for subsystems
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid_full
        main_sys.tags = ['experiment id: '+uid_pre,'date: '+t_str,'utc: '+str(int(t_utc))]
        self.outputs['pif'] = main_sys

    def saxs_to_pif_properties(self,q_I,T_C):
        #props = []
        #for i in range(len(q)):
        pq = pifobj.Property()
        n_qpoints = q_I.shape[0]
        ### property: scattered intensity
        pI = pifobj.Property()
        pI.name = 'SAXS intensity'
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = 'counts'
        pI.conditions = []
        pI.conditions.append( pifobj.Value('SAXS scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,'1/Angstrom') )
        pI.conditions.append(pifobj.Value('temperature',[pifobj.Scalar(T_C)],None,None,'degrees Celsius'))
        return [pq,pI] 
        
#    def make_piftemperature(self,t):
#        v = pifobj.Value()
#        v.name = 'temperature'
#        tscl = pifobj.Scalar()
#        tscl.value = str(t)
#        v.scalars = [tscl]
#        v.units = 'degrees Celsius'
#        return v
#
#    def make_pifvector(self,v):
#        pifv = []
#        for n in v:
#            s = pifobj.Scalar()
#            s.value = str(n)
#            pifv.append(s)
#        return pifv
#
#    def pifscalar(self,scl,errlo,errhi):
#        s = pifobj.Scalar()
#        s.value = str(scl) 
#        s.minimum = str(scl) 
#        s.maximum = str(scl) 
#        s.inclusiveMinimum = True
#        s.inclusiveMaximum = True
#        s.uncertainty = '+{},-{}'.format(errlo,errhi)
#        s.approximate = True
#        return s



