from .PawsPlugin import PawsPlugin
from ..workflow.WfManager import WfManager 

class WfManagerPlugin(PawsPlugin):
    """
    This plugin exposes the content of the workflow manager.
    """

    def __init__(self):
        input_names = ['wf_manager']
        super(WfManagerPlugin,self).__init__(input_names)
        self.input_doc['wf_manager'] = 'A workflow manager (paws.core.workflow.WfManager.WfManager).'

    def start(self):
        self.wfman = self.inputs['wf_manager'] 
        pass 

    def stop(self):
        pass

    def content(self):
        if isinstance(self.wfman,WfManager):
            return self.wfman.workflows
        else:
            return {} 

    def description(self):
        return str('Workflow manager Plugin for paws: '
            + 'This wraps the workflow manager in a plugin, '
            + 'so that workflows can use the plugin '
            + 'to fetch data from other workflows.')


