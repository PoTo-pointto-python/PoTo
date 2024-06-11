from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_execfile import FixExecfile

def test_PT_FixExecfile_transform():
    f = FixExecfile()
    f.transform()
