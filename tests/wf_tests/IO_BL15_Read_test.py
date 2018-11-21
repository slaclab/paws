import os

from paws.workflows.IO.BL15.Read import Read
from paws import pawstools

tdd = os.path.join(pawstools.rootdir,'tests','test_data')

def test():
    read_wf = Read()
    outs = read_wf.run_with(
        time_key = 't_utc',
        header_file = os.path.join(tdd,'headers','test1.yml'),
        image_file = os.path.join(tdd,'images','test1.tif'),
        q_I_file = os.path.join(tdd,'data','test1.dat'),
        system_file = os.path.join(tdd,'systems','test1.yml')
        )
    return True

