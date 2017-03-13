from ..operations import optools
from .. import pawstools
from .plugin import PawsPlugin
from ..workflow.workflow import Workflow

class WorkflowPlugin(PawsPlugin):
    """
    Wrapper contains a workflow and 
    implements the PawsPlugin abc interface.
    This Plugin is generated programmatically
    when the WfManager creates or loads a new Workflow.
    """
    # TODO: Make this work with .wfl input from the filesystem

    def __init__(self):
        input_names = ['workflow']
        super(WorkflowPlugin,self).__init__(input_names)
        self.input_src['workflow'] = optools.fs_input
        self.input_type['workflow'] = optools.path_type
        self.input_doc['workflow'] = str('This can be either the path to a .wfl file on the filesystem, '
        + 'or a workflow can be loaded to this location automatically '
        + 'when a new Workflow is created by the workflow manager (WfManager).')

    def start(self):
        self.wf = self.inputs['workflow'] 
        pass 

    def stop(self):
        pass

    def content(self):
        #wf_dict = {'workflow':self.wf}

        #return wf_dict
        if isinstance(self.wf,Workflow):
            return {itm.tag():self.wf.build_dict(itm) for itm in self.wf.root_items}
        else:
            return {}

    def description(self):
        desc = str('Workflow Plugin for paws: '
            + 'This wraps a workflow in a plugin, providing its operations as tree content '
            + 'so that other workflows and plugins can gain access to them.')
        return desc


