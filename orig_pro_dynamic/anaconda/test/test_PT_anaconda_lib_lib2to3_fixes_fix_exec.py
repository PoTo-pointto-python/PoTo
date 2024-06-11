from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_exec import FixExec

def test_PT_FixExec_transform():
    f = FixExec()
    f.transform()
