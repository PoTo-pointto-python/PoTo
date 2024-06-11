from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_set_literal import FixSetLiteral

def test_PT_FixSetLiteral_transform():
    f = FixSetLiteral()
    f.transform()
