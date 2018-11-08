import os

from paws.workflows.IO.BL15.LEGACY.Read import Read
from paws import pawstools

tdd = os.path.join(pawstools.rootdir,'tests','test_data')

def test():
    read_wf = Read()
    outs = read_wf.run_with(
        header_file = os.path.join(tdd,'headers','legacy','test1.txt'),
        image_file = os.path.join(tdd,'images','test1.tif'),
        q_I_file = os.path.join(tdd,'data','test1.dat'),
        system_file = os.path.join(tdd,'systems','test1.yml')
        )
    return True

