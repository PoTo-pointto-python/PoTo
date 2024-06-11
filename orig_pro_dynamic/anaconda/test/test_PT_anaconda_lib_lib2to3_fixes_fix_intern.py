from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_intern import FixIntern

def test_PT_FixIntern_transform():
    f = FixIntern()
    f.transform()