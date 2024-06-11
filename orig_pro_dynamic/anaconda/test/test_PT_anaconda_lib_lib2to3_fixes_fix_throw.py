from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_throw import FixThrow

def test_PT_FixThrow_transform():
    f = FixThrow()
    f.transform()
