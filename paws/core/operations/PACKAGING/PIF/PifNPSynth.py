import numpy as np
import pypif.obj as pifobj

from ... import Operation as op
from ...Operation import Operation

class PifNPSynth(Operation):
    """
    Package results from nanoparticle solution synthesis into a pypif.obj.ChemicalSystem object.
    """

    def __init__(self):
        input_names = ['uid_prefix','date_time','t_utc','temp_C','q_I','t_T','composition','features']
        output_names = ['pif']
        super(PifNPSynth,self).__init__(input_names,output_names)
        self.input_doc['uid_prefix'] = 'text string to prepend to pif uid (pif uid = uid_prefix+t_utc'
        self.input_doc['date_time'] = 'string date/time from measurement header file for pif record tags'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['temp_C'] = 'temperature in degrees C'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities for saxs spectrum'
        self.input_doc['t_T'] = 'n-by-2 array of time (in seconds utc) and corresponding temperatures'
        self.input_doc['composition'] = 'dict describing recipe, in the format of IO.MISC.ReadNPSynthRecipe'
        self.input_doc['features'] = str('dict describing spectrum features, in the format of '
        + 'PROCESSING.SAXS.[SpectrumProfiler,SpectrumParameterization].')
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_src['uid_prefix'] = op.text_input
        self.input_src['date_time'] = op.wf_input
        self.input_src['t_utc'] = op.wf_input
        self.input_src['temp_C'] = op.wf_input
        self.input_src['q_I'] = op.wf_input
        self.input_src['t_T'] = op.wf_input
        self.input_src['composition'] = op.wf_input
        self.input_src['features'] = op.wf_input
        self.input_type['uid_prefix'] = op.str_type
        self.input_type['date_time'] = op.ref_type
        self.input_type['t_utc'] = op.ref_type
        self.input_type['temp_C'] = op.ref_type
        self.input_type['q_I'] = op.ref_type
        self.input_type['t_T'] = op.ref_type
        self.input_type['composition'] = op.ref_type
        self.input_type['features'] = op.ref_type

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = uid_pre+'_'+str(int(t_utc))
        temp_C = self.inputs['temp_C']
        q_I = self.inputs['q_I']
        t_T = self.inputs['t_T']
        c = self.inputs['composition']
        f = self.inputs['features']
        # Subsystems for solution ingredients
        #colloid_sys = pifobj.ChemicalSystem(uid_pre+'_pd_colloid',['colloidal Pd nanoparticles'],None,None,None,'Pd') 
        #acid_sys = pifobj.ChemicalSystem(uid_pre+'_oleic_acid',['oleic acid'],None,None,None,'C18H34O2') 
        #amine_sys = pifobj.ChemicalSystem(uid_pre+'_oleylamine',['oleylamine'],None,None,None,'C18H35NH2') 
        #TOP_sys = pifobj.ChemicalSystem(uid_pre+'_trioctylphosphine',['trioctylphosphine'],None,None,None,'P(C8H17)3')
        #subsys = [colloid_sys,acid_sys,amine_sys,TOP_sys]
        # TODO: Quantity information for subsystems
        main_sys = pifobj.ChemicalSystem()
        main_sys.uid = uid_full
        #main_sys.sub_systems = subsys
        if q_I is not None and temp_C is not None:
            main_sys.properties = self.saxs_to_pif_properties(q_I,temp_C)
        main_sys.tags = ['reaction id: '+uid_pre,'date: '+t_str,'utc: '+str(int(t_utc))]
        self.outputs['pif'] = main_sys

    def saxs_to_pif_properties(self,q_I,temp_C):
        #props = []
        #for i in range(len(q)):
        #pq = pifobj.Property()
        ### property: scattered intensity
        pI = pifobj.Property()
        pI.name = 'SAXS intensity'
        n_qpoints = q_I.shape[0]
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = 'counts'
        pI.conditions = []
        pI.conditions.append( pifobj.Value('SAXS scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,None,'1/Angstrom') )
        pI.conditions.append(pifobj.Value('temperature',[pifobj.Scalar(temp_C)],None,None,None,'degrees Celsius'))
        return [pI] 
        
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


