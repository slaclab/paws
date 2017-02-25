from ..operations import optools
from .. import pawstools
from plugin import PawsPlugin

class WorkflowPlugin(PawsPlugin):
    """
    Wrapper contains a workflow and 
    implements the PawsPlugin abc interface.
    """

    def __init__(self,wf):
        super(WorkflowPlugin,self).__init__(input_names)
        self.wf = wf 

    def start(self):
        pass 

    def stop(self):
        pass

    def content(self): 
        # TODO: wf._wf_dict was meant to be private or no?
        return self.wf.build_dict(self.wf._wf_dict)

    def description(self):
        desc = str('Workflow Plugin for paws: '
            + 'This container stores a reference to a workflow in a plugin, '
            + 'so that other workflows and plugins can gain access to it.')
        return desc


