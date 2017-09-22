import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation

class EmptyPif(Operation):
    """
    Make and empty pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['uid','date_time','t_utc']
        output_names = ['pif']
        super(EmptyPif,self).__init__(input_names,output_names)
        self.input_doc['uid'] = 'text string to use as pif record uid'
        self.input_doc['date_time'] = 'string date/time for pif record tags'
        self.input_doc['t_utc'] = 'time of record creation in utc'
        self.output_doc['pif'] = 'an empty pif object'
        self.input_type['date_time'] = opmod.workflow_item
        self.input_type['t_utc'] = opmod.workflow_item

    def run(self):
        uid = self.inputs['uid']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        if uid is None:
            return
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid
        main_sys.tags = ['experiment id: '+uid]
        if t_str is not None:
            main_sys.tags.append('date: '+t_str)
        if t_utc is not None:
            main_sys.tags.append('utc: '+str(int(t_utc)))
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



