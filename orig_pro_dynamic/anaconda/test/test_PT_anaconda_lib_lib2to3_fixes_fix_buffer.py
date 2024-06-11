from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_buffer import FixBuffer

def test_PT_FixBuffer_transform():
    f = FixBuffer()
    f.transform()
