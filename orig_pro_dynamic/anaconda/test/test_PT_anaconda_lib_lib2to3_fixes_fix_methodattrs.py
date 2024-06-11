from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_methodattrs import FixMethodattrs

def test_PT_FixMethodattrs_transform():
    f = FixMethodattrs()
    f.transform()