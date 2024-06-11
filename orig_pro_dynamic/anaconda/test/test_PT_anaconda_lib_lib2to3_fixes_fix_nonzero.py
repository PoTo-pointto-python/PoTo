from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_nonzero import FixNonzero

def test_PT_FixNonzero_transform():
    f = FixNonzero()
    f.transform()