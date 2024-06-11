from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_unicode import FixUnicode

def test_PT_FixUnicode_transform():
    f = FixUnicode()
    f.transform()
