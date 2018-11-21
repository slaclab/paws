import os

from paws.workflows.IO.BL15.ReadTimeSeries import ReadTimeSeries
from paws import pawstools

tdd = os.path.join(pawstools.rootdir,'tests','test_data')

def test():
    tsread_wf = ReadTimeSeries()
    outs = tsread_wf.run_with(
        time_key = 't_utc',
        header_dir = os.path.join(tdd,'headers'),
        header_regex = '*.yml',
        image_dir = os.path.join(tdd,'images'),
        q_I_dir = os.path.join(tdd,'data'),
        system_dir = os.path.join(tdd,'systems')
        )
    return True

