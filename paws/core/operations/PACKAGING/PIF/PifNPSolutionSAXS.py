import numpy as np
import pypif.obj as pifobj

from ... import Operation as opmod 
from ...Operation import Operation
from ....tools import saxstools

class PifNPSolutionSAXS(Operation):
    """
    Package SAXS results from a nanoparticle solution into a pypif.obj.ChemicalSystem record.
    """

    def __init__(self):
        input_names = ['uid_prefix','date_time','t_utc','q_I','temperature','features']
        output_names = ['pif']
        super(PifNPSolutionSAXS,self).__init__(input_names,output_names)
        self.input_doc['uid_prefix'] = 'text string to prepend to pif uid (pif uid = uid_prefix+t_utc'
        self.input_doc['date_time'] = 'string date/time from measurement header file, used for pif record tags'
        self.input_doc['t_utc'] = 'time in seconds utc'
        self.input_doc['q_I'] = 'n-by-2 array of q values and corresponding intensities for saxs spectrum'
        self.input_doc['temperature'] = 'temperature of the system in degrees Celsius'
        self.input_doc['features'] = 'dict of features extracted from the measured spectrum.'
        self.output_doc['pif'] = 'pif object representing the input data'
        self.input_type['date_time'] = opmod.workflow_item
        self.input_type['t_utc'] = opmod.workflow_item
        self.input_type['q_I'] = opmod.workflow_item
        self.input_type['temperature'] = opmod.workflow_item
        self.input_type['features'] = opmod.workflow_item
        # all inputs default to none: an empty pif should be produced in this case.
        self.inputs['uid_prefix'] = None
        self.inputs['date_time'] = None
        self.inputs['t_utc'] = None
        self.inputs['q_I'] = None
        self.inputs['temperature'] = None
        self.inputs['features'] = None

    def run(self):
        uid_pre = self.inputs['uid_prefix']
        t_str = self.inputs['date_time']
        t_utc = self.inputs['t_utc']
        uid_full = 'tmp'
        if uid_pre is not None:
            uid_full = uid_pre
        if t_utc is not None:
            uid_full = uid_full+'_'+str(int(t_utc))
        temp_C = self.inputs['temperature']
        q_I = self.inputs['q_I']
        ftrs = self.inputs['features']

        # ChemicalSystem record construction begins here
        csys = pifobj.ChemicalSystem()
        csys.uid = uid_full
        csys.properties = []
        csys.tags = []
        if uid_pre is not None:
            csys.tags.append('reaction id: '+uid_pre)
        if t_str is not None:
            csys.tags.append('date: '+t_str)
        if t_utc is not None:
            csys.tags.append('utc: '+str(int(t_utc)))

        # TODO: include the scattering equation in this record somehow
        if ftrs is not None:
            if ftrs['bad_data']:
                csys.tags.append('unidentified scattering or bad data')
            if ftrs['diffraction_peaks']:
                csys.tags.append('diffraction peaks')
            if ftrs['form_factor_scattering']:
                csys.tags.append('form factor scattering')
                if not ftrs['diffraction_peaks'] and not ftrs['bad_data']:
                    csys.properties.append(self.feature_property(None,'nanoparticle mean radius','Angstrom'))
                    csys.properties.append(self.feature_property(None,'fractional standard deviation of nanoparticle radius',''))
                    csys.properties.append(self.feature_property(None,'form factor scattering intensity prefactor','counts'))
            if ftrs['precursor_scattering']:
                csys.tags.append('precursor scattering')
                if not ftrs['diffraction_peaks'] and not ftrs['bad_data']:
                    csys.properties.append(self.feature_property(None,'precursor effective radius','Angstrom'))
                    csys.properties.append(self.feature_property(None,'precursor scattering intensity prefactor','counts'))

        if q_I is not None:
            # Process measured q_I into a property
            pI = self.q_I_property(q_I)
            if temp_C is not None:
                pI.conditions.append(pifobj.Value('temperature',[pifobj.Scalar(temp_C)],None,None,None,'degrees Celsius'))
            pI.name = 'SAXS intensity' 
            csys.properties.append(pI)
            if not ftrs['diffraction_peaks'] and not ftrs['bad_data']:
                csys.properties.append(self.feature_property(None,'scattered intensity at q=0','counts'))
                # Compute the saxs spectrum, package it
                qI_computed = saxstools.compute_saxs(q_I[:,0],ftrs)
                pI_computed = self.q_I_property(np.array( [[q_I[i,0],qI_computed[i]] for i in range(len(qI_computed))] ))
                pI_computed.name = 'computed SAXS intensity'
                csys.properties.append(pI_computed)
        self.outputs['pif'] = csys

    def feature_property(self,fval,fname,funits=''):
        pf = pifobj.Property()
        pf.name = fname
        pf.scalars = [pifobj.Scalar(fval)]
        if funits:
            pf.units = funits
        return pf

    def q_I_property(self,q_I):
        pI = pifobj.Property()
        n_qpoints = q_I.shape[0]
        pI.scalars = [pifobj.Scalar(q_I[i,1]) for i in range(n_qpoints)]
        pI.units = 'counts'
        pI.conditions = []
        pI.conditions.append( pifobj.Value('scattering vector', 
                            [pifobj.Scalar(q_I[i,0]) for i in range(n_qpoints)],
                            None,None,None,'1/Angstrom') )
        return pI 
        
