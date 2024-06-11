from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_xreadlines import FixXreadlines

def test_PT_FixXreadlines_transform():
    f = FixXreadlines()
    f.transform()
