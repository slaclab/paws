import numpy as np
import pypif.obj as pifobj

from ... import Operation as op
from ...Operation import Operation

class PifTernary(Operation):
    """
    Package results from ternary wafer synthesis into a pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['name','q_I','q_texture','I_features','pk_idx','date_time','t_utc']
        output_names = ['pif']
        super(PifTernary,self).__init__(input_names,output_names)
        self.input_doc['name'] = 'user input string used as pif record uid'
        self.input_doc['q_I'] = 'array of q and I(q) values for xrd spectrum'
        self.input_doc['q_texture'] = 'array of q and texture(q) for xrd spectrum'
        self.input_doc['I_features'] = 'output of IntensityFeatures operation, providing Imax, Iave, Imax_Iave_ratio'
        self.input_doc['pk_idx'] = 'indices in q,I where peaks can be found'
        self.input_doc['date_time'] = 'string date/time from measurement header file for pif record tags'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_src['name'] = op.text_input
        self.input_src['q_I'] = op.wf_input
        self.input_src['q_texture'] = op.wf_input
        self.input_src['I_features'] = op.wf_input
        self.input_src['pk_idx'] = op.wf_input
        self.input_src['date_time'] = op.wf_input
        self.input_src['t_utc'] = op.wf_input
        self.input_type['name'] = op.str_type
        self.input_type['q_I'] = op.ref_type
        self.input_type['q_texture'] = op.ref_type
        self.input_type['I_features'] = op.ref_type
        self.input_type['pk_idx'] = op.ref_type
        self.input_type['date_time'] = op.ref_type
        self.input_type['t_utc'] = op.ref_type
        self.output_doc['pif'] = 'pif object containing the relevant data for this experiment'

    def run(self):
        uid_pre = self.inputs['name']
        q_I = self.inputs['q_I']
        q_tex = self.inputs['q_texture']
        I_feats = self.inputs['I_features']
        pk_idx = self.inputs['pk_idx']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = uid_pre+'_'+str(int(t_utc))
        q = q_I[:,0]
        I_of_q = q_I[:,1]
        q_pk = np.array([q[idx] for idx in pk_idx])
        I_pk = np.array([I_of_q[idx] for idx in pk_idx])
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid_full
        main_sys.properties = self.xrd_to_pif_properties(q,I_of_q)
        main_sys.properties += self.texture_to_pif_properties(q_tex[:,0],q_tex[:,1])
        main_sys.properties += self.pks_to_pif_properties(q_pk,I_pk)
        main_sys.properties += self.intensity_features_to_pif_properties(I_feats)
        main_sys.tags = ['sample id: '+uid_pre,'date: '+t_str,'utc: '+str(int(t_utc))]
        self.outputs['pif'] = main_sys

    def intensity_features_to_pif_properties(self,I_feats):
        pImax = pifobj.Property()
        pImax.name = 'maximum XRD intensity'
        pImax.scalars = [ pifobj.Scalar(I_feats['Imax']) ]
        pImax.units = 'counts'
        pIave = pifobj.Property()
        pIave.name = 'average XRD intensity'
        pIave.scalars = [ pifobj.Scalar(I_feats['Iave']) ]
        pIave.units = 'counts'
        pratio = pifobj.Property()
        pratio.name = 'maximum-over-average XRD intensity'
        pratio.scalars = [ pifobj.Scalar(I_feats['Imax_Iave_ratio']) ]
        pratio.units = 'unitless'
        return [pImax,pIave,pratio] 

    def pks_to_pif_properties(self,q_pk,I_pk):
        props = []
        for i in range(len(q_pk)):
            p = pifobj.Property()
            p.name = 'XRD peak'
            p.scalars = [ pifobj.Scalar(I_pk[i]) ]
            p.conditions = [] 
            p.conditions.append( pifobj.Value('scattering vector',[pifobj.Scalar(q_pk[i])],None,None,'Angstrom^-1') )
            p.units = 'counts'
            props.append(p)
        return props

    def texture_to_pif_properties(self,q,tex_q):
        props = []
        for i in range(len(q)):
            p = pifobj.Property()
            p.name = 'texture'
            p.scalars = [ pifobj.Scalar(tex_q[i]) ]
            p.conditions = [] 
            p.conditions.append( pifobj.Value('scattering vector',[pifobj.Scalar(q[i])],None,None,'Angstrom^-1') )
            p.units = 'counts'
            props.append(p)
        return props

    def xrd_to_pif_properties(self,q,I_q):
        props = []
        for i in range(len(q)):
            p = pifobj.Property()
            p.name = 'XRD intensity'
            p.scalars = [ pifobj.Scalar(I_q[i]) ]
            p.conditions = [] 
            p.conditions.append( pifobj.Value('scattering vector',[pifobj.Scalar(q[i])],None,None,'Angstrom^-1') )
            p.units = 'counts'
            props.append(p)
        return props
        
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


