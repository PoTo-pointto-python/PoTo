from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_has_key import FixHasKey

def test_PT_FixHasKey_transform():
    f = FixHasKey()
    f.transform()
