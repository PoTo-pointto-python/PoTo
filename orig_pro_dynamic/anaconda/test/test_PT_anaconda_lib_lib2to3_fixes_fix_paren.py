from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_paren import FixParen

def test_PT_FixParen_transform():
    f = FixParen()
    f.transform()