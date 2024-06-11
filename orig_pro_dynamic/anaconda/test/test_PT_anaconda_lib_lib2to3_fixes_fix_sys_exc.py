from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_sys_exc import FixSysExc

def test_PT_FixSysExc_transform():
    f = FixSysExc()
    f.transform()
