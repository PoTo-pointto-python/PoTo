from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_funcattrs import FixFuncattrs

def test_PT_FixFuncattrs_transform():
    f = FixFuncattrs()
    f.transform()
