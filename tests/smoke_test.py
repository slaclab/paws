import paws
from paws import operations
from paws import workflows
from paws import plugins

from paws.operations import Operation, \
    ARRAYS, BACKGROUND, CALIBRATION, FILESYSTEM, SMOOTHING, \
    SORTING, SSRL_BEAMLINE_1_5, TESTS, ZINGERS
from paws.operations.ARRAYS import ArrayYMean, NoiseArray
from paws.operations.BACKGROUND import BgSubtract
from paws.operations.CALIBRATION import ReadPONI, Fit2DToPONI, NikaToPONI, WXDToPONI 
from paws.operations.FILESYSTEM import BuildFileList 
from paws.operations.SMOOTHING import MovingAverage, SavitzkyGolay 
from paws.operations.SORTING import SortBatch 
from paws.operations.SSRL_BEAMLINE_1_5 import ReadSpecHeader
from paws.operations.TESTS import Print, ListPrimes
from paws.operations.ZINGERS import EasyZingers1d 

from paws.workflows import Workflow, SSRL_BEAMLINE_1_5
from paws.workflows.SSRL_BEAMLINE_1_5 import Read, ReadBatch, ReadTimeSeries
from paws.workflows.SSRL_BEAMLINE_1_5 import LEGACY 
from paws.workflows.SSRL_BEAMLINE_1_5.LEGACY import Read, ReadBatch, ReadTimeSeries

from paws.plugins import PawsPlugin, \
    BayesianDesigner, CitrinationClient, CitrinationDesigner, CryoConController, \
    FlowReactor, MarCCDClient, MitosPPumpController, PyFAIIntegrator, SpecInfoClient, \
    SSHClient, Timer 

def test_imports():
    return True

