from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_repr import FixRepr

def test_PT_FixRepr_transform():
    f = FixRepr()
    f.transform()
